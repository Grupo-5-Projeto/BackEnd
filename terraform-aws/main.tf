terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

}

provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "vpc_terraform" {
  cidr_block           = "10.0.0.0/24"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "vpc-upaconnect"
  }
}

resource "aws_subnet" "public_subnet_av1" {
  depends_on = [aws_vpc.vpc_terraform]

  vpc_id                  = aws_vpc.vpc_terraform.id
  cidr_block              = "10.0.0.0/26"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "sub-pub-av1-upaconnect"
  }
}

resource "aws_internet_gateway" "igw-upaconnect" {
  depends_on = [
    aws_vpc.vpc_terraform,
    aws_subnet.public_subnet_av1
  ]

  vpc_id = aws_vpc.vpc_terraform.id

  tags = {
    Name = "igw-upaconnect"
  }
}

resource "aws_route_table" "rtb_main_upaconnect" {
  depends_on = [
    aws_vpc.vpc_terraform,
    aws_subnet.public_subnet_av1,
    aws_internet_gateway.igw-upaconnect
  ]

  vpc_id = aws_vpc.vpc_terraform.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw-upaconnect.id
  }

  route {
    ipv6_cidr_block = "::/0"
    gateway_id      = aws_internet_gateway.igw-upaconnect.id
  }

  tags = {
    Name = "rtb-main-upaconnect"
  }
}

resource "aws_route_table_association" "rta_public_subnet_1" {
  subnet_id      = aws_subnet.public_subnet_av1.id
  route_table_id = aws_route_table.rtb_main_upaconnect.id
}

resource "aws_security_group" "sg_access_instance" {
  name        = "access-upaconnect"
  description = "Ec2 upa"
  vpc_id      = aws_vpc.vpc_terraform.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "access-ec2-upaconnect"
  }
}

resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "chave-upaconnect"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

resource "aws_instance" "instance_jupiter_1" {
  ami           = "ami-0866a3c8686eaeeba"
  instance_type = "t2.medium"
  key_name      = aws_key_pair.generated_key.key_name

  subnet_id                   = aws_subnet.public_subnet_av1.id
  associate_public_ip_address = true
  security_groups             = [aws_security_group.sg_access_instance.id]

  ebs_block_device {
    device_name = "/dev/sda1"
    volume_size = 30
    volume_type = "gp3"
  }

  tags = {
    Name = "instance-1"
  }

}

resource "aws_s3_bucket" "s3_stage" {
  bucket = "bucket-upaconnect-stage"

  tags = {
    Name = "Stage"
  }
}

resource "aws_s3_bucket" "s3_trusted" {
  bucket = "bucket-upaconnect-trusted"

  tags = {
    Name = "Trusted"
  }
}

resource "aws_s3_bucket" "s3_client" {
  bucket = "bucket-upaconnect-client"

  tags = {
    Name = "Client"
  }
}

resource "aws_s3_bucket_policy" "allow_access_1" {
  bucket = aws_s3_bucket.s3_stage.id
  policy = data.aws_iam_policy_document.allow_access_bucket_stage.json
}

resource "aws_s3_bucket_policy" "allow_access_2" {
  bucket = aws_s3_bucket.s3_trusted.id
  policy = data.aws_iam_policy_document.allow_access_bucket_trusted.json
}

resource "aws_s3_bucket_policy" "allow_access_3" {
  bucket = aws_s3_bucket.s3_client.id
  policy = data.aws_iam_policy_document.allow_access_bucket_client.json
}

data "aws_iam_policy_document" "allow_access_bucket_client" {
  depends_on = [
    aws_s3_bucket.s3_client,
  ]
  statement {
    principals {
      type        = "AWS"
      identifiers = ["810673762812"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.s3_client.arn,
      "${aws_s3_bucket.s3_client.arn}/*"
    ]
  }
}

data "aws_iam_policy_document" "allow_access_bucket_stage" {
  depends_on = [
    aws_s3_bucket.s3_client,
  ]
  statement {
    principals {
      type        = "AWS"
      identifiers = ["810673762812"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.s3_stage.arn,
      "${aws_s3_bucket.s3_stage.arn}/*"
    ]
  }
}

data "aws_iam_policy_document" "allow_access_bucket_trusted" {
  depends_on = [
    aws_s3_bucket.s3_client,
  ]
  statement {
    principals {
      type        = "AWS"
      identifiers = ["810673762812"]
    }

    actions = [
      "s3:GetObject"
    ]

    resources = [
      aws_s3_bucket.s3_trusted.arn,
      "${aws_s3_bucket.s3_trusted.arn}/*"
    ]
  }
}

