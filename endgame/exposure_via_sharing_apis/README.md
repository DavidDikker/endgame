# Resource that can be made public through sharing APIs


## Support Status

### AMI
Actions:
- ec2 [modify-image-attribute](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ec2/modify-image-attribute.html)

### EBS snapshot
Actions:
- ec2 [modify-snapshot-attribute](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ec2/modify-snapshot-attribute.html)
  - [moto modify_snapshot_attribute](https://github.com/spulec/moto/blob/master/moto/ec2/responses/elastic_block_store.py#L129)
  - [moto describe_snapshot_attribute](https://github.com/spulec/moto/blob/master/moto/ec2/responses/elastic_block_store.py#L122)

### RDS snapshot
Actions:
- rds [modify-db-snapshot](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/rds/modify-db-snapshot.html)
  - [CLI to share a snapshot](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ShareSnapshot.html#USER_ShareSnapshot.Sharing)


## Not supported (yet)

### FPGA image
Actions:
- ec2 [modify-fpga-image-attribute](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ec2/modify-fpga-image-attribute.html)

### RDS DB Cluster snapshot
Actions:
- rds [modify-db-cluster-snapshot-attribute](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/rds/modify-db-cluster-snapshot-attribute.html)