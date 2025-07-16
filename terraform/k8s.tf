resource "scaleway_vpc_private_network" "pn" {
  name       = "tf-pn"
  project_id = var.organisation_id
  region     = var.region
}

resource "scaleway_k8s_cluster" "cluster" {
  name                        = "tf-cluster"
  version                     = "1.32.3"
  cni                         = "cilium"
  private_network_id          = scaleway_vpc_private_network.pn.id
  delete_additional_resources = false
  project_id                  = var.organisation_id
  region                      = var.region

  autoscaler_config {
    disable_scale_down              = false
    scale_down_delay_after_add      = "5m"
    scale_down_unneeded_time        = "5m"
    estimator                       = "binpacking"
    expander                        = "random"
    ignore_daemonsets_utilization   = true
    balance_similar_node_groups     = true
    expendable_pods_priority_cutoff = -10
  }
}

resource "scaleway_k8s_pool" "pool" {
  cluster_id        = scaleway_k8s_cluster.cluster.id
  name              = "tf-pool"
  node_type         = "GP1-XS"
  size              = 2
  container_runtime = "containerd"
}

output "cluster_id" {
  value = scaleway_k8s_cluster.cluster.id
}