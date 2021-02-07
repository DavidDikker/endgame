output "snapshot_identifier" {
  value = aws_db_cluster_snapshot.test_resource_exposure.db_cluster_identifier
}

output "arn" {
  value = aws_db_cluster_snapshot.test_resource_exposure.db_cluster_snapshot_arn
}