resource "aws_db_instance" "bar" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t2.micro"
  name                 = "mydb"
  username             = "foo"
  password             = "foobarbaz"
  parameter_group_name = "default.mysql5.7"
  multi_az = true
  db_subnet_group_name = aws_db_subnet_group.default.name
}
//resource "aws_db_instance" "bar" {
//  allocated_storage = 10
//  engine            = "MySQL"
//  engine_version    = "5.7"
//  instance_class    = "db.t2.micro"
//  name              = var.name
//  password          = "barbarbarbar"
//  username          = "foo"
//
//  maintenance_window      = "Fri:09:00-Fri:09:30"
//  backup_retention_period = 0
//  parameter_group_name    = "default.mysql5.6"
//}

resource "aws_db_snapshot" "test" {
  db_instance_identifier = aws_db_instance.bar.id
  db_snapshot_identifier = "${var.name}-db"
}

resource "aws_vpc" "main" {
  cidr_block       = "10.0.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "subnet_1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.1/28"
  availability_zone = "us-east-1b"

  tags = {
    Name = "subnet_1"
  }
}

resource "aws_subnet" "subnet_2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.16/28"
  availability_zone = "us-east-1c"

  tags = {
    Name = "subnet_1"
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "test-resource-exposure-subnet"
  subnet_ids = [aws_subnet.subnet_1.id, aws_subnet.subnet_2.id]

  tags = {
    Name = "test-resource-exposure"
  }
}