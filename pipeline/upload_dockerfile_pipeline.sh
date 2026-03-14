# Step 1: Authenticate Docker to ECR
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

# Step 2: Create an ECR repository, if it doesn't already exist
aws ecr create-repository --repository-name c22-jessh-etl-ecr --region eu-west-2 2>/dev/null || true

# Step 3: Build your Docker image
docker build --platform linux/amd64 --provenance=false -t c22-jessh-etl-ecr .

# Step 4: Tag your Docker image
docker tag c22-jessh-etl-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c22-jessh-etl-ecr:latest

# Step 5: Push the image to ECR
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c22-jessh-etl-ecr:latest