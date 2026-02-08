#!/usr/bin/env python3.9
import os
import subprocess
import sys

# ========= CONFIGURACIÓN =========
TEAM_ID = "27"
APP_OWNER = "Moreno-et-al"

IMAGE_NAME = f"cdps-productpage:g{TEAM_ID}"
CONTAINER_NAME = f"productpage_cdps_{TEAM_ID}"
HOST_PORT = "9095"
CONTAINER_PORT = "8080"

REPO_URL = "https://github.com/CDPS-ETSIT/practica_creativa2.git"
BASE_DIR = "practica_creativa2/bookinfo/src/productpage"
PRODUCTPAGE_FILE = os.path.join(BASE_DIR, "productpage_monolith.py")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates/index.html")
DOCKERFILE_PATH = os.path.join(BASE_DIR, "Dockerfile")
# =================================


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        sys.exit(1)


def clone_repo():
    if not os.path.isdir("practica_creativa2"):
        run(["git", "clone", REPO_URL])

def patch_productpage_py():

    with open(PRODUCTPAGE_FILE, "r") as f:
        content = f.read()

    if "TEAM_ID = os.getenv" not in content:
        content = content.replace(
            "import os",
            "import os\n\nTEAM_ID = os.getenv(\"TEAM_ID\", \"unknown\")\nAPP_OWNER = os.getenv(\"APP_OWNER\", \"unknown\")"
        )

    if "render_template(\n        'productpage.html'," in content and "app_owner=APP_OWNER" not in content:
        content = content.replace(
            "return render_template(\n        'productpage.html',",
            "return render_template(\n        'productpage.html',\n        team_id=TEAM_ID,\n        app_owner=APP_OWNER,"
        )

    content = content.replace(
        "return render_template('index.html', serviceTable=table)",
        "return render_template('index.html', serviceTable=table, team_id=TEAM_ID, app_owner=APP_OWNER)"
    )

    with open(PRODUCTPAGE_FILE, "w") as f:
        f.write(content)


def patch_template():

    with open(TEMPLATE_FILE, "r") as f:
        content = f.read()

    content = content.replace(
        "Simple Bookstore App",
        "Product Page - {{ app_owner }} - Team {{ team_id }}"
    )

    with open(TEMPLATE_FILE, "w") as f:
        f.write(content)


def create_dockerfile():

    dockerfile = """FROM python:3.9-slim

WORKDIR /opt/productpage

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python3", "productpage_monolith.py", "8080"]
"""
    with open(DOCKERFILE_PATH, "w") as f:
        f.write(dockerfile)


def build_image():
    run(["docker", "build", "-t", IMAGE_NAME, "."], cwd=BASE_DIR)


def run_container():
    subprocess.run(
        ["docker", "rm", "-f", CONTAINER_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    run([
        "docker", "run",
        "--name", CONTAINER_NAME,
        "-p", f"{HOST_PORT}:{CONTAINER_PORT}",
        "-e", f"TEAM_ID={TEAM_ID}",
        "-e", f"APP_OWNER={APP_OWNER}",
        "-d", IMAGE_NAME
    ])


def main():

    clone_repo()
    patch_productpage_py()
    patch_template()
    create_dockerfile()
    build_image()
    run_container()


    print(f" Play With Docker → Open Port → {HOST_PORT}")
    print(f" http://<IP>:{HOST_PORT}/productpage")


if __name__ == "__main__":
    main()
