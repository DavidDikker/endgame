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
  multi_az             = true
  db_subnet_group_name = aws_db_subnet_group.default.name
  skip_final_snapshot  = true
}


resource "aws_db_snapshot" "test" {
  db_instance_identifier = aws_db_instance.bar.id
  db_snapshot_identifier = var.name
}

resource "aws_vpc" "main" {
  cidr_block       = "10.0.0.0/16"
  instance_tenancy = "default"

  tags = {
    Name = "main"
  }
}

resource "aws_subnet" "subnet_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/28"
  availability_zone = "us-east-1b"

  tags = {
    Name = "subnet_1"
  }
}

resource "aws_subnet" "subnet_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.16/28"
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