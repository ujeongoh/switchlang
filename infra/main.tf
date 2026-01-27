# 1. Kind Cluster Resource
resource "kind_cluster" "default" {
  name           = var.cluster_name
  node_image     = var.node_image
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"
      
      # Port mapping for Ingress (Host 80 -> Container 80)
      extra_port_mappings {
        container_port = 80
        host_port      = 80
        protocol       = "TCP"
      }
      extra_port_mappings {
        container_port = 443
        host_port      = 443
        protocol       = "TCP"
      }
    }
  }
}

# 2. Helm & Kubernetes Providers Configuration
provider "helm" {
  kubernetes {
    config_path = kind_cluster.default.kubeconfig_path
  }
}

provider "kubernetes" {
  config_path = kind_cluster.default.kubeconfig_path
}

# 3. Nginx Ingress Controller Installation
resource "helm_release" "ingress_nginx" {
  name             = "ingress-nginx"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  
  depends_on = [kind_cluster.default]

  # Configuration for Kind environment
  set {
    name  = "controller.hostPort.enabled"
    value = "true"
  }
  set {
    name  = "controller.service.type"
    value = "NodePort"
  }
  set {
    name  = "controller.publishService.enabled"
    value = "false"
  }
}

# 4. ArgoCD Installation
resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  create_namespace = true

  depends_on = [kind_cluster.default]

  # Disable TLS for local development convenience
  set {
    name  = "server.extraArgs"
    value = "{--insecure}"
  }
}