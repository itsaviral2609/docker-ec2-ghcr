# Flask Application Deployment on AWS Ec2 & Publishing to ghcr

![Screenshot from 2025-02-25 13-50-18](https://github.com/user-attachments/assets/50b3ad9d-dc9b-4a16-bd36-a41a09dad4f3)


## Overview
This guide covers the process of building a **Flask application** into a **Docker image**, pushing it to **GitHub Container Registry (ghcr)**, and deploying it on an **AWS EC2 instance** using **GitHub Actions**.

## Prerequisites
1. **AWS EC2 Instance** with Ubuntu.
2. **GitHub Repository** to store the project.
3. **GitHub Actions** enabled.
4. **Docker Installed** on the local machine & EC2 instance.
5. **GitHub Container Registry (ghcr) Access**.
6. **Secrets configured** in GitHub:
   - `EC2_HOST`: Public IP of EC2.
   - `EC2_USER`: Username for EC2 instance.
   - `EC2_PRIVATE_KEY`: SSH private key for EC2 access.
   - `GITHUB_TOKEN`: GitHub token for authentication.

## Project Structure

```sh
/docker-ec2-ghcr
│── app.py
│── Dockerfile
│── requirements.txt
│── .github/
│    └── workflows/
│        └── main.yml
```

## Dockerfile
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["python", "app.py"]
```

## GitHub Actions Workflow
### **deploy.yml** (Located in `.github/workflows/`)
This workflow automates the CI/CD pipeline, including:
1. **Build & Push Image to GHCR** on a `push` to the `main` branch.
2. **Deploy to EC2** after the image is pushed.

```yaml
name: Flask application deployment on EC2 and publish to GHCR

on:
  push:
    branches:
      - main

jobs:
  # Step 1: Build and push the Docker image to GHCR
  build_and_push:
    name: Build image and push
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Building Flask application Dockerfile
        run: docker build -t ghcr.io/${{ github.repository_owner }}/flask-image:latest .

      - name: Pushing Flask application to GHCR
        run: docker push ghcr.io/${{ github.repository_owner }}/flask-image:latest

  # Step 2: Deploy on EC2
  deploy:
    name: Deploy on EC2 instance
    runs-on: ubuntu-latest
    needs: build_and_push

    steps:
      - name: SSH into EC2 and Deploy
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_PRIVATE_KEY }}
          script: |
            # Update package list
            sudo apt update

            # Install Docker if not already installed
            if ! command -v docker &> /dev/null
            then
                sudo apt install -y docker.io
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo usermod -aG docker $USER
            fi

            # Restart Docker service to ensure it is running
            sudo systemctl restart docker

            sudo chmod 666 /var/run/docker.sock

            # Ensure the user has permission to run Docker commands
            newgrp docker || true

            # Log in to GHCR inside EC2 instance
            echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin

            # Pull the latest image
            docker pull ghcr.io/${{ github.repository_owner }}/flask-image:latest

            # Stop and remove existing container (if running)
            docker stop flask-app || true
            docker rm flask-app || true

            # Run the new container
            docker run -d -p 5000:5000 --name flask-app ghcr.io/${{ github.repository_owner }}/flask-image:latest
```

## Steps to Deploy
1. **Push code to GitHub** (`git push origin main`).
2. **GitHub Actions Workflow runs automatically**:
   - **Step 1:** Builds and pushes the image to GHCR.
   - **Step 2:** Logs into EC2, pulls the image, and deploys it.
3. **Application is now running on EC2** and accessible on `http://EC2_PUBLIC_IP:5000`.

## Verifying Deployment
To check if the container is running on EC2:
```sh
ssh -i your-key.pem ec2-user@EC2_HOST

docker ps  # Check running containers
curl http://localhost:5000  # Test Flask app
```

# Expected Result

![Screenshot from 2025-02-18 16-12-49](https://github.com/user-attachments/assets/0956f5cb-3e60-49aa-a5bf-6a626f3e763c)

![Screenshot from 2025-02-18 16-15-01](https://github.com/user-attachments/assets/02392a8f-4284-4b97-a8cb-e209259701c2)


## Conclusion
This setup ensures an automated CI/CD pipeline for Flask applications using **GitHub Actions, ghcr, and AWS EC2**, making deployments seamless and efficient.
