# Configure Terraform version and required providers for the infrastructure
terraform {
  # Specify required providers and their versions
  required_providers {
    # Kind provider: Used to create and manage local Kubernetes clusters
    # Allows spinning up a fully containerized Kubernetes cluster for development
    kind = {
      source  = "tehcyx/kind"
      version = "0.2.1"
    }
    
    # Helm provider: Used to deploy and manage Helm charts on Kubernetes clusters
    # Enables declarative management of Kubernetes applications via Helm
    helm = {
      source  = "hashicorp/helm"
      version = "2.12.1"
    }
    
    # Kubernetes provider: Used to interact with Kubernetes API resources
    # Allows managing Kubernetes objects like namespaces, services, etc.
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.24.0"
    }
  }
}

# Initialize the Kind provider with default configuration
provider "kind" {}