resource "aws_rds_cluster" "test_resource_exposure" {
  cluster_identifier      = var.name
  engine                  = "aurora-mysql"
  engine_version          = "5.7.mysql_aurora.2.03.2"
  availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
  database_name           = "mydb"
  master_username         = "foo"
  master_password         = "bar"
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
}

resource "aws_db_cluster_snapshot" "test_resource_exposure" {
  db_cluster_identifier          = aws_rds_cluster.test_resource_exposure.id
  db_cluster_snapshot_identifier = "test-resource-exposure-cluster"
}