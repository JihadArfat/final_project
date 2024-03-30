# DevOps Final Project
## Overview
This project represents the culmination of our journey through the DevOps lifecycle, aiming to integrate modern technologies and best practices for efficient application deployment, scaling, monitoring, and management within Kubernetes clusters hosted on AWS. Additionally, CI/CD processes are streamlined using Jenkins to ensure seamless code integration and continuous delivery.

## Technologies Used
Kubernetes: Container orchestration platform for automating deployment, scaling, and management of containerized applications.

AWS: Cloud platform providing a range of cloud services, including EC2 instances, EBS volumes, and managed Kubernetes service (EKS).

Ingress-Nginx: Open-source Kubernetes Ingress controller that manages external access to services within a Kubernetes cluster.

Grafana: Open-source platform for monitoring and observability with customizable dashboards.

Prometheus: Open-source monitoring and alerting toolkit designed for reliability, scalability, and robustness.

FluentD: Data collection and log forwarding for better log management and analytics.

Helm: Kubernetes package manager for defining, installing, and upgrading Kubernetes applications.

Jenkins: Open-source automation server used for CI/CD processes to automate the build, test, and deployment pipeline.

## Setup and Installation
### Prerequisites
#### * AWS account with necessary permissions
#### * kubectl installed
#### * Helm installed
#### * Jenkins installed and configured

## Steps
#### 1. Setting up Kubernetes Cluster on AWS:

##### * Create an EKS cluster using AWS Management Console or CLI.
##### * Configure kubectl to connect to the EKS cluster.

#### 2. Installing Ingress-Nginx:

#### 3. Deploying Applications:
Use kubectl apply to deploy your applications.


#### 4. Setting up CI/CD with Jenkins:

Install necessary plugins in Jenkins.
Configure Jenkins pipelines for building, testing, and deploying your applications.

#### 5. Monitoring with Grafana and Prometheus:
Deploy Grafana and Prometheus using Helm.

## Usage
After completing the setup and installation, you can access your applications through the configured domain and monitor their performance and logs using Grafana and Prometheus dashboards.
