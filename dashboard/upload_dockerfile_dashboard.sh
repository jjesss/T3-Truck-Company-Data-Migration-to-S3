# Build Image
docker build --platform linux/amd64 -f dockerfile -t c22-jessh-t3-dashboard .

# Tag Image
docker tag c22-jessh-t3-dashboard:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c22-jessh-t3-dashboard:latest

# Push Image
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c22-jessh-t3-dashboard:latest