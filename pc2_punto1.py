#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/CDPS-ETSIT/practica_creativa2.git"
INSTALL_DIR = Path("/opt/practica_creativa2")
VENV_DIR = INSTALL_DIR / ".venv"
PRODUCTPAGE_DIR = INSTALL_DIR / "bookinfo/src/productpage"
MONOLITH = PRODUCTPAGE_DIR / "productpage_monolith.py"
TEMPLATES_DIR = PRODUCTPAGE_DIR / "templates"
SERVICE_PATH = Path("/etc/systemd/system/cdps-productpage.service")

def run(cmd, check=True, capture=False):
    cmd = [str(x) for x in cmd]
    print("+", " ".join(cmd))
    if capture:
        return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return subprocess.run(cmd, check=check)

def sh(cmd, check=True, capture=False):
    print("+", cmd)
    if capture:
        return subprocess.run(cmd, shell=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return subprocess.run(cmd, shell=True, check=check)

def require_root():
    if os.geteuid() != 0:
        raise SystemExit("ERROR: ejecuta con sudo: sudo /usr/bin/python3.9 ~/pc2_punto1.py ...")

def check_python39():
    print("== CHECK: Python usado ==")
    print("sys.executable:", sys.executable)
    print("sys.version:", sys.version.replace("\n", " "))
    if sys.version_info[:2] != (3, 9):
        raise SystemExit("ERROR: no estás usando Python 3.9. Usa: sudo /usr/bin/python3.9 ~/pc2_punto1.py ...")

def clean_previous():
    print("== 0) Limpieza previa (reproducible) ==")
    sh("systemctl stop cdps-productpage 2>/dev/null || true", check=False)
    sh("systemctl disable cdps-productpage 2>/dev/null || true", check=False)
    sh("systemctl reset-failed cdps-productpage 2>/dev/null || true", check=False)
    sh(f"rm -rf {INSTALL_DIR}", check=False)
    sh(f"rm -f {SERVICE_PATH}", check=False)
    sh("systemctl daemon-reload", check=False)

def install_deps():
    print("== 1) Dependencias de sistema ==")
    run(["apt-get", "update"])
    run([
        "apt-get", "install", "-y", "-qq",
        "-o", "Dpkg::Options::=--force-confdef",
        "-o", "Dpkg::Options::=--force-confold",
        "git", "ca-certificates", "curl",
        "python3-pip", "python3-setuptools", "python3.9-venv",
    ])

def clone_repo():
    print("== 2) Clonando repositorio (como root en /opt) ==")
    if INSTALL_DIR.exists():
        raise SystemExit(f"ERROR: {INSTALL_DIR} ya existe. Usa --clean o bórralo.")
    run(["git", "clone", REPO_URL, str(INSTALL_DIR)])

def setup_venv():
    print("== 3) venv Python 3.9 + requirements ==")
    run(["/usr/bin/python3.9", "-m", "venv", str(VENV_DIR)])
    run([str(VENV_DIR / "bin/python"), "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"])
    run([str(VENV_DIR / "bin/pip"), "install", "-r", str(PRODUCTPAGE_DIR / "requirements.txt")])

    # Verificación: el venv realmente es 3.9
    out = run([str(VENV_DIR / "bin/python"), "-c", "import sys; print(sys.version_info[:2])"], capture=True).stdout.strip()
    if out != "(3, 9)":
        raise SystemExit(f"ERROR: el venv no es Python 3.9 (sale {out}).")

def modify_host_in_productpage():
    # Ubicación del archivo productpage_monolith.py
    file_path = "/opt/practica_creativa2/bookinfo/src/productpage/productpage_monolith.py"
    
    # Abrir el archivo en modo lectura
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Buscar la línea que contiene el `app.run()` y reemplazarla con la configuración adecuada
    updated_content = re.sub(r"app.run\(host='[^']+', port=p, debug=True, threaded=True\)",
                             "app.run(host='0.0.0.0', port=p, debug=True, threaded=True)", 
                             file_content)

    # Escribir el contenido actualizado en el archivo
    with open(file_path, 'w') as file:
        file.write(updated_content)
    
    print("El archivo productpage_monolith.py ha sido actualizado para escuchar en 0.0.0.0")

def patch_monolith_team_id():
    print("== 4) Parcheando productpage_monolith.py para pasar TEAM_ID a templates ==")
    if not MONOLITH.exists():
        raise SystemExit(f"ERROR: no existe {MONOLITH}")

    text = MONOLITH.read_text(encoding="utf-8")

    # 1) Localizar fin de bloques __future__ (si existe)
    m = re.search(r"^(from __future__ import .+\n)+", text, flags=re.M)
    insert_at = m.end() if m else 0

    # 2) Asegurar que HAY "import os" ANTES de insertar TEAM_ID_VALUE
    #    (aunque exista otro import os más abajo, no vale)
    head = text[:insert_at]
    has_import_os_before = re.search(r"^\s*import\s+os(\s|,|$)", head, flags=re.M) is not None
    has_from_os_before = re.search(r"^\s*from\s+os\s+import\s+", head, flags=re.M) is not None

    if not (has_import_os_before or has_from_os_before):
        text = text[:insert_at] + "import os\n" + text[insert_at:]
        insert_at += len("import os\n")

    # 3) Insertar TEAM_ID_VALUE una sola vez (justo tras ese insert_at)
    if 'TEAM_ID_VALUE = os.environ.get("TEAM_ID"' not in text:
        line = 'TEAM_ID_VALUE = os.environ.get("TEAM_ID", "UNKNOWN_TEAM")\n'
        text = text[:insert_at] + line + text[insert_at:]
        insert_at += len(line)

    # 4) Añadir TEAM_ID=TEAM_ID_VALUE a render_template de index.html/productpage.html
    def add_kw(match):
        inside = match.group(1)
        if re.search(r"\bTEAM_ID\s*=", inside):
            return match.group(0)
        if not re.search(r"['\"](?:index|productpage)\.html['\"]", inside):
            return match.group(0)
        return f"render_template({inside}, TEAM_ID=TEAM_ID_VALUE)"

    text = re.sub(r"render_template\(([^)]*)\)", add_kw, text)

    # 5) ESCRIBIR el fichero antes de validar/compilar
    MONOLITH.write_text(text, encoding="utf-8")

    # 6) Validación: compila (evita IndentationError)
    run([str(VENV_DIR / "bin/python"), "-m", "py_compile", str(MONOLITH)])

    # 7) Validación adicional: comprobar que quedó TEAM_ID_VALUE en fichero
    new_text = MONOLITH.read_text(encoding="utf-8")
    if 'TEAM_ID_VALUE = os.environ.get("TEAM_ID"' not in new_text:
        raise SystemExit("ERROR: no quedó insertado TEAM_ID_VALUE en el monolito.")

    print(f"OK: parche aplicado: {MONOLITH}")

def patch_template_block_title(path: Path):
    html = path.read_text(encoding="utf-8")

    # Reemplaza el bloque title (si existe)
    html2, n = re.subn(
        r"\{%\s*block\s+title\s*%\}.*?\{%\s*endblock\s*%\}",
        "{% block title %}{{ TEAM_ID }} - Simple Bookstore App{% endblock %}",
        html,
        count=1,
        flags=re.I | re.S,
    )
    if n == 0:
        raise SystemExit(f"ERROR: No encontré el bloque Jinja 'title' en {path}")

    path.write_text(html2, encoding="utf-8")
    print(f"OK: block title parcheado: {path}")

def patch_templates():
    print("== 4b) Parcheando templates (block title) ==")
    productpage_tpl = TEMPLATES_DIR / "productpage.html"
    index_tpl = TEMPLATES_DIR / "index.html"

    if not productpage_tpl.exists():
        raise SystemExit(f"ERROR: no existe {productpage_tpl}")
    if not index_tpl.exists():
        raise SystemExit(f"ERROR: no existe {index_tpl}")

    patch_template_block_title(productpage_tpl)
    patch_template_block_title(index_tpl)

def ensure_permissions():
    print("== 5) Permisos para ejecutar como ubuntu ==")
    run(["chown", "-R", "ubuntu:ubuntu", str(INSTALL_DIR)])

def write_systemd_service(team_id: str, port: int):
    print("== 6) Creando servicio systemd y arrancando ==")
    unit = f"""[Unit]
Description=CDPS BookInfo Productpage (monolith)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory={PRODUCTPAGE_DIR}
Environment=TEAM_ID={team_id}
ExecStart={VENV_DIR}/bin/python {MONOLITH} {port}
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
"""
    SERVICE_PATH.write_text(unit, encoding="utf-8")
    run(["systemctl", "daemon-reload"])
    run(["systemctl", "enable", "--now", "cdps-productpage"])

def final_checks(port: int):
    print("== 7) Checks finales ==")
    sh("systemctl status cdps-productpage --no-pager -l", check=False)

    # Espera hasta 10s a que el endpoint responda (evita falsos negativos)
    sh(
        f"bash -lc 'for i in {{1..20}}; do "
        f"curl -fsS -o /dev/null http://127.0.0.1:{port}/productpage && exit 0; "
        f"sleep 0.5; "
        f"done; exit 1'",
        check=False,
    )

    sh(f"curl -I http://127.0.0.1:{port}/productpage", check=False)
    sh(f"curl -s http://127.0.0.1:{port}/productpage | grep -i '<title' || true", check=False)
    sh(f"curl -s http://127.0.0.1:{port}/productpage | tr '\\n' ' ' | grep -oi '<title[^>]*>[^<]*</title>' || true", check=False)

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--team-id", required=True, help="TEAM_ID (p.ej. GRUPO_27)")
    ap.add_argument("--port", type=int, required=True, help="Puerto (NO 9090)")
    ap.add_argument("--clean", action="store_true", help="Borra instalación previa y servicio")
    return ap.parse_args()

def main():
    args = parse_args()
    require_root()
    check_python39()

    if args.clean:
        clean_previous()

    install_deps()
    clone_repo()
    setup_venv()
# Modificar el archivo productpage_monolith.py para escuchar en todas las interfaces
    modify_host_in_productpage()
    patch_monolith_team_id()
    patch_templates()
    ensure_permissions()
    write_systemd_service(args.team_id, args.port)
    final_checks(args.port)

if __name__ == "__main__":
    main()
