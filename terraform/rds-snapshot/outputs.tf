output "snapshot_identifier" {
  value = aws_db_snapshot.test.db_snapshot_identifier
}

output "arn" {
  value = aws_db_snapshot.test.db_snapshot_arn
}