# Creative Practice 2 – CDPS

This repository contains the implementation of **Creative Practice 2** for the course **CDPS (Concepts and Design of Digital Systems)**.

The objective of this practice is to explore and compare different application deployment strategies, evolving from a traditional monolithic deployment to container-based and microservices-oriented architectures, and finally introducing container orchestration.

The practice is based on the **BookInfo** application and focuses on deployment automation, system configuration, and architectural design.

---

## Project Overview

The work is structured into four main stages:

1. Deployment of a monolithic application on a virtual machine
2. Deployment of a monolithic application using Docker
3. Segmentation of the application into microservices using Docker Compose
4. Deployment of the microservices-based application using Kubernetes

The emphasis of the practice is placed on understanding the differences between deployment models and their implications in terms of scalability, maintainability, and fault tolerance.

---

## 1. Deployment on a Virtual Machine

In the first stage, the application is deployed on a Linux virtual machine hosted on **Google Cloud**.

A **Python 3.9 deployment script** automates the full installation and configuration process, including:
- Installation of system dependencies
- Cloning the application repository
- Creation of a Python virtual environment
- Installation of required libraries
- Application startup on a non-default port

The application reads the `TEAM_ID` value from an environment variable, which is injected through a **systemd service**. This allows the application to start automatically on boot and to restart in case of failure.

This deployment serves as a baseline reference for comparison with container-based approaches.

---

## 2. Monolithic Deployment Using Docker

In the second stage, the application is deployed as a **monolithic Docker container**.

A Python script automates the entire process:
- Cloning the repository from GitHub
- Modifying the application to accept environment variables (`TEAM_ID` and `APP_OWNER`)
- Automatically generating a `Dockerfile`
- Building the Docker image
- Running the container (removing any previous container with the same name if necessary)

The application is exposed through a configurable port and can be accessed once the container is running.

This approach highlights the limitations of monolithic architectures, particularly regarding fault tolerance and scalability.

---

## 3. Microservices Deployment Using Docker Compose

In the third stage, the application is restructured following a **microservices architecture** and deployed using **Docker Compose**.

The system is composed of the following independent services:
- **Product Page (Python)**: frontend service coordinating requests to the rest of the system
- **Details (Ruby)**: provides detailed information about the book
- **Reviews**: manages user reviews and communicates with the ratings service
- **Ratings (Node.js)**: provides numerical ratings

Each microservice runs in its own Docker container. Docker Compose automatically creates an internal virtual network that enables service-to-service communication using service names instead of fixed IP addresses.

### Requirements
- Docker
- Docker Compose

### Build
```bash
docker-compose -f docker-compose.micro.yml build

Run
docker-compose -f docker-compose.micro.yml up

Access
http://localhost:9080

Stop
docker-compose -f docker-compose.micro.yml down

This deployment demonstrates the benefits of microservices in terms of modularity, scalability, and maintainability.

**## 4. Microservices Deployment Using Kubernetes**

The microservices-based version of the application was successfully deployed using Kubernetes through Google Cloud Console.

The deployment is defined using a set of Kubernetes configuration files, where each microservice is deployed independently and exposed through its corresponding service definition. External access to the application is provided through a load balancer.

The Kubernetes configuration includes the following files:

productpage-deployment-g27

productpage-service-g27

productpage-loadbalancer-g27

details-deployment-g27

details-service-g27

reviews-deployment-g27

reviews-service-g27

ratings-deployment-g27

ratings-service-g27

These files describe the deployments and services required to run the BookInfo application in a Kubernetes-managed environment, enabling inter-service communication and external access.

This stage completes the transition from a monolithic architecture to a fully containerized and orchestrated microservices deployment.

**DISCLAIMER:**
This repository is shared voluntarily for educational and demonstrative purposes
