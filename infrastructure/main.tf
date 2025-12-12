provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type for benchmarking"
  type        = string
  default     = "t3.medium"
}

variable "github_repo" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/gmzrmz/proyecto-final-ada"
}

variable "algorithms" {
  description = "List of algorithms to benchmark"
  type        = list(string)
  default     = [
    "brute_force",
    "backtracking",
    "divide_and_conquer",
    "memoization",
    "tabulation"
  ]
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "matrix-crossing-benchmark"
}

variable "docker_image" {
  description = "Docker image for running benchmarks"
  type        = string
  default     = "gmzrmz/matrix-benchmark:latest"
}

variable "use_aws_academy" {
  description = "Set to true if using AWS Academy (uses LabRole instead of creating IAM role)"
  type        = bool
  default     = true
}

variable "experiment_id" {
  description = "Unique experiment ID (timestamp)"
  type        = string
  default     = ""
}

# S3 bucket for storing benchmark results
# Always create a new unique bucket per experiment run
resource "aws_s3_bucket" "results" {
  bucket        = var.experiment_id != "" ? "${var.project_name}-${var.experiment_id}" : "${var.project_name}-${formatdate("YYYYMMDDhhmmss", timestamp())}"
  force_destroy = true  # Permite destruir el bucket aunque tenga archivos

  tags = {
    Name        = "${var.project_name}-experiment"
    Environment = "benchmark"
    ExperimentID = var.experiment_id
  }
}

locals {
  bucket_id = aws_s3_bucket.results.id
  bucket_arn = aws_s3_bucket.results.arn
}

resource "aws_s3_bucket_versioning" "results" {
  count = var.use_aws_academy ? 0 : 1
  bucket = local.bucket_id

  versioning_configuration {
    status = "Enabled"
  }
}

# Use existing LabRole for AWS Academy
data "aws_iam_role" "lab_role" {
  count = var.use_aws_academy ? 1 : 0
  name  = "LabRole"
}

# IAM role for EC2 instances (only if NOT using AWS Academy)
resource "aws_iam_role" "ec2_benchmark" {
  count = var.use_aws_academy ? 0 : 1
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ec2_s3_upload" {
  count = var.use_aws_academy ? 0 : 1
  name = "${var.project_name}-s3-upload"
  role = aws_iam_role.ec2_benchmark[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          local.bucket_arn,
          "${local.bucket_arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_benchmark" {
  count = var.use_aws_academy ? 0 : 1
  name = "${var.project_name}-instance-profile"
  role = aws_iam_role.ec2_benchmark[0].name
}

# Use existing LabInstanceProfile for AWS Academy
data "aws_iam_instance_profile" "lab_profile" {
  count = var.use_aws_academy ? 1 : 0
  name  = "LabInstanceProfile"
}

locals {
  instance_profile_name = var.use_aws_academy ? data.aws_iam_instance_profile.lab_profile[0].name : aws_iam_instance_profile.ec2_benchmark[0].name
}

# Security group for EC2 instances
resource "aws_security_group" "benchmark" {
  name        = "${var.project_name}-sg-${var.experiment_id}"
  description = "Security group for benchmark EC2 instances"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# Get latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

# EC2 instances (one per algorithm)
resource "aws_instance" "benchmark" {
  count = length(var.algorithms)

  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  iam_instance_profile   = local.instance_profile_name
  vpc_security_group_ids = [aws_security_group.benchmark.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    algorithm_name = var.algorithms[count.index]
    s3_bucket      = local.bucket_id
    github_repo    = var.github_repo
    experiment_id  = var.experiment_id
  })

  tags = {
    Name        = "${var.project_name}-${var.algorithms[count.index]}"
    Algorithm   = var.algorithms[count.index]
    Environment = "benchmark"
    ExperimentID = var.experiment_id
  }

  # Terminate after completion
  instance_initiated_shutdown_behavior = "terminate"
}

# Outputs
output "bucket_name" {
  description = "S3 bucket name for results"
  value       = local.bucket_id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = local.bucket_arn
}

output "instance_ids" {
  description = "EC2 instance IDs"
  value       = { for idx, instance in aws_instance.benchmark : var.algorithms[idx] => instance.id }
}

output "instance_public_ips" {
  description = "Public IP addresses of EC2 instances"
  value       = { for idx, instance in aws_instance.benchmark : var.algorithms[idx] => instance.public_ip }
}
