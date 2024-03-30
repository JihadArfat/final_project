DevOps Final Project
Overview
This project represents the culmination of our journey through the DevOps lifecycle, aiming to integrate modern technologies and best practices for efficient application deployment, scaling, monitoring, and management within Kubernetes clusters hosted on AWS. Additionally, CI/CD processes are streamlined using Jenkins to ensure seamless code integration and continuous delivery.

Technologies Used
Kubernetes: Container orchestration platform for automating deployment, scaling, and management of containerized applications.

AWS: Cloud platform providing a range of cloud services, including EC2 instances, EBS volumes, and managed Kubernetes service (EKS).

Ingress-Nginx: Open-source Kubernetes Ingress controller that manages external access to services within a Kubernetes cluster.

Grafana: Open-source platform for monitoring and observability with customizable dashboards.

Prometheus: Open-source monitoring and alerting toolkit designed for reliability, scalability, and robustness.

FluentD: Data collection and log forwarding for better log management and analytics.

Helm: Kubernetes package manager for defining, installing, and upgrading Kubernetes applications.

Jenkins: Open-source automation server used for CI/CD processes to automate the build, test, and deployment pipeline.

Setup and Installation
Prerequisites
AWS account with necessary permissions
kubectl installed
Helm installed
Jenkins installed and configured
Steps
Setting up Kubernetes Cluster on AWS:

Create an EKS cluster using AWS Management Console or CLI.
Configure kubectl to connect to the EKS cluster.
Installing Ingress-Nginx:

bash
Copy code
helm install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress --set controller.ingressClassResource.name=nginx --set controller.service.type=LoadBalancer --set controller.service.externalTrafficPolicy=Local
Deploying Applications:

Use kubectl apply to deploy your applications.
bash
Copy code
kubectl apply -f your-application.yaml
Setting up CI/CD with Jenkins:

Install necessary plugins in Jenkins.
Configure Jenkins pipelines for building, testing, and deploying your applications.
Monitoring with Grafana and Prometheus:

Deploy Grafana and Prometheus using Helm.
bash
Copy code
helm install prometheus stable/prometheus --namespace monitoring
helm install grafana grafana/grafana --namespace monitoring
Usage
After completing the setup and installation, you can access your applications through the configured domain and monitor their performance and logs using Grafana and Prometheus dashboards.

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
