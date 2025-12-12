#!/bin/bash
set -e  # Exit on error
set -x  # Debug mode
exec > >(tee /var/log/user-data.log) 2>&1

echo "=== Starting user_data script ==="
echo "Algorithm: ${algorithm_name}"
echo "S3 Bucket: ${s3_bucket}"
echo "GitHub Repo: ${github_repo}"
echo "Experiment ID: ${experiment_id}"
echo "Timestamp: $(date)"

# Install Docker
echo "=== Installing Docker ==="
curl -fsSL https://get.docker.com -o get-docker.sh || { echo "Failed to download Docker installer"; exit 1; }
sh get-docker.sh || { echo "Failed to install Docker"; exit 1; }

# Wait for Docker to be ready
echo "=== Waiting for Docker ==="
sleep 10
systemctl start docker || { echo "Failed to start Docker"; exit 1; }
systemctl enable docker

# Verify Docker is running
echo "=== Verifying Docker ==="
docker --version || { echo "Docker not working"; exit 1; }

# Pull Python image and run inline
echo "=== Running benchmark in Docker container ==="
docker run --rm \
  -e ALGORITHM="${algorithm_name}" \
  -e S3_BUCKET="${s3_bucket}" \
  -e GITHUB_REPO="${github_repo}" \
  -e EXPERIMENT_ID="${experiment_id}" \
  -e AWS_DEFAULT_REGION=us-east-1 \
  python:3.11-slim \
  bash -c '
    set -e
    echo "Inside container - starting"
    
    # Install dependencies
    echo "Installing dependencies..."
    apt-get update -y
    apt-get install -y git curl unzip zip
    
    echo "Installing AWS CLI..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o aws.zip
    unzip -q aws.zip
    ./aws/install
    
    # Clone repo and setup
    echo "Cloning repository..."
    git clone "$GITHUB_REPO" /app
    cd /app
    
    # Update to latest code
    echo "Updating to latest code..."
    git pull origin main
    
    echo "Installing Python dependencies..."
    pip install --no-cache-dir -r requirements.txt
    
    # Download matrices
    echo "Downloading matrices from S3..."
    mkdir -p /matrices
    /usr/local/bin/aws s3 cp "s3://$S3_BUCKET/test_matrices.tar.gz" /matrices/
    cd /matrices
    tar -xzf test_matrices.tar.gz
    
    # Run unit tests BEFORE benchmarking (Python handles everything including S3 upload on failure)
    cd /app
    if ! python src/benchmark/unit_test_report.py "$ALGORITHM" "/results" "$EXPERIMENT_ID" "$S3_BUCKET"; then
        echo "Unit tests FAILED - report uploaded to S3"
        exit 1
    fi
    
    # Mark benchmark start time
    date +%s > /results/.benchmark_start_time
    
    # Run benchmark
    echo "Running benchmark for $ALGORITHM..."
    python run_benchmark.py --algorithm "$ALGORITHM" --output /results --matrices-dir /matrices/test_matrices
    
    # Upload results (Python handles metadata generation, ZIP creation, and S3 upload)
    echo "Uploading results to S3..."
    python src/benchmark/upload_results.py "$EXPERIMENT_ID" "$ALGORITHM" "$S3_BUCKET"
  '

DOCKER_EXIT=$?
echo "=== Docker container exited with code: $DOCKER_EXIT ==="

if [ $DOCKER_EXIT -eq 0 ]; then
  echo "=== SUCCESS - Benchmark completed ==="
  echo "Shutting down instance..."
  shutdown -h now
else
  echo "=== ERROR - Benchmark failed ==="
  echo "NOT shutting down to allow debugging"
  # Keep instance running for 1 hour for debugging
  sleep 3600
fi
