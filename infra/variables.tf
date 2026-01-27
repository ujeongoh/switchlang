variable "cluster_name" {
  description = "The name of the Kind cluster"
  type        = string
  default     = "switchlang-cluster"
}

variable "node_image" {
  description = "Docker image for the Kind node (Kubernetes version)"
  type        = string
  default     = "kindest/node:v1.27.3"
}