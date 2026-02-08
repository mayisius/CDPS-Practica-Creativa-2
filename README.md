# Creative Practice 2 – Scalable Application Deployment (CDPS)

This repository contains the implementation of **Creative Practice 2** for the course  
**CDPS – Concepts and Design of Digital Systems**.

The objective of this practice is to design and deploy a **reliable and scalable application** using multiple deployment technologies commonly used in modern **DevOps and cloud environments**.

The work is based on the **BookInfo** application provided by the course and focuses on comparing different deployment strategies, from traditional virtual machines to container orchestration with Kubernetes.

---

## Objectives

- Deploy a monolithic application using traditional virtual machines
- Deploy the same application using Docker (lightweight virtualization)
- Refactor the application into a microservices architecture using Docker Compose
- Deploy the microservices-based application using Kubernetes
- Understand the trade-offs between the different deployment approaches in terms of scalability, reliability, and maintainability

---

## Deployment Stages

### 1. Monolithic Deployment on a Virtual Machine
The application is deployed as a monolith on a Linux virtual machine hosted on **Google Cloud**.

A **Python 3.9 script** automates the installation of dependencies, application setup, configuration of environment variables (`TEAM_ID`), and service management using **systemd**, ensuring persistence and automatic restart.

---

### 2. Monolithic Deployment Using Docker
The same monolithic application is deployed using **Docker**, packaging the service into a single container.

A Python script automates:
- Repository cloning
- Environment variable injection (`TEAM_ID`, `APP_OWNER`)
- Dockerfile generation
- Image building and container execution

This stage demonstrates the benefits of containerization compared to traditional VM-based deployments.

---

### 3. Microservices Deployment Using Docker Compose
The application is restructured following a **microservices architecture**, separating functionality into independent services:

- Product Page (Python)
- Details (Ruby)
- Reviews (Java)
- Ratings (Node.js)

Each service runs in its own container and is orchestrated using **Docker Compose**, enabling internal communication through a dedicated virtual network.

---

### 4. Microservices Deployment Using Kubernetes
The microservices-based application is deployed using **Kubernetes** through **Google Cloud Console**.

Each microservice is deployed independently and exposed through its corresponding service. External access to the application is provided via a load balancer, completing the transition to a fully orchestrated and scalable deployment.

---

## Repository Structure

The repository is organized according to the four main stages of the practice:

### Point 1 – Virtual Machine Deployment
- `pc2_punto1`  
  Python script for deploying the monolithic application on a virtual machine.

### Point 2 – Docker Monolithic Deployment
- `deploy_productpage_docker`  
  Python script that automates the Docker-based deployment of the monolithic application.

### Point 3 – Docker Compose (Microservices)
- `docker-compose.micro`
- `Dockerfile` (one per microservice)

Configuration files for building and orchestrating the microservices architecture using Docker Compose.

### Point 4 – Kubernetes Deployment
- `productpage-deployment-g27`
- `productpage-service-g27`
- `productpage-loadbalancer-g27`
- `details-deployment-g27`
- `details-service-g27`
- `reviews-deployment-g27`
- `reviews-service-g27`
- `ratings-deployment-g27`
- `ratings-service-g27`

Kubernetes configuration files defining the deployments and services required to run the application in a Kubernetes cluster.

---

## Notes

- This repository is shared voluntarily for educational purposes
- The original written report is not included to preserve student privacy
- No personal or sensitive information is contained in this repository
