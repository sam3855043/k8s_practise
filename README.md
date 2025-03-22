# Flask Library Management System with Kubernetes

A Flask-based library management system with MySQL database, containerized with Docker and orchestrated by Kubernetes.

## Project Structure
```
k8s_practise/
├── libaray_service_py_mysql/  # Main application directory
│   ├── app.py                 # Flask application
│   ├── templates/             # HTML templates
│   └── static/               # Static files
├── flask-deployment.yaml      # Kubernetes deployment config
└── service.yaml              # Kubernetes service config
```

## Deployment Guide

### 1. Docker Setup
```bash
# Build Docker image
docker build -t flask-book-app .

# Run container locally
docker run -d -p 5010:5010 flask-book-app

# Debug container
docker exec -it <container_id> /bin/bash
docker logs <container_id>
```

### 2. Kubernetes Deployment

#### Minikube Setup
```bash
# Start minikube
minikube start --driver=docker

# Load image into minikube
minikube image load flask-book-app
```

#### Deploy Application
```bash
# Apply configurations
kubectl apply -f flask-deployment.yaml
kubectl apply -f service.yaml

# Verify deployment
kubectl get pods
kubectl get services

# Access the application
minikube service flask-service
# or
minikube service flask-service --url
```

#### Quick Deploy (Without YAML)
```bash
kubectl run mypod --image=flask-book-app --image-pull-policy=Never --port=5010
kubectl port-forward pod/mypod 5010:5010
```

### 3. Kubernetes Commands Reference

| Operation | Command |
|-----------|---------|
| Deploy Flask service | `kubectl apply -f flask-service.yaml` |
| Check service status | `kubectl get services` |
| Test service (Minikube) | `minikube service flask-service` |
| View pod details | `kubectl describe pod <pod-name>` |
| View logs | `kubectl logs <pod-name>` |
| Edit service | `kubectl edit service flask-service` |
| Scale deployment | `kubectl scale deployment flask-app --replicas=<number>` |

## Docker Command Guide

### Docker Run vs Start

| Feature | `docker run` | `docker start` |
|---------|-------------|----------------|
| Creates new container | ✅ Yes | ❌ No |
| Starts existing container | ❌ No | ✅ Yes |
| Assigns new ID | ✅ Yes | ❌ No |
| Keeps existing config | ❌ No | ✅ Yes |

### Common Docker Commands
```bash
# Inspect container
docker inspect <container_id>

# Execute commands in container
docker exec -it <container_id> /bin/bash

# View container logs
docker logs <container_id>
```

## Troubleshooting

### MacOS Docker Issues
1. Reset Docker environment:
```bash
eval $(minikube docker-env)
unset DOCKER_HOST
```

2. Restart Docker:
```bash
osascript -e 'quit app "Docker"'
open /Applications/Docker.app
```

3. Check Docker status:
```bash
docker info
docker ps
```

### Common Issues Resolution
1. Connection issues: Check if Docker daemon is running
2. Image pull failures: Verify image exists locally
3. Pod startup failures: Check logs with `kubectl logs`
4. Service access issues: Verify service configuration and ports

## Configuration Files

### Service Configuration (service.yaml)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-flask-book-app
spec:
  selector:
    app: flask-book-app
  ports:
    - protocol: TCP
      port: 5010
      targetPort: 5010
      nodePort: 30510
  type: NodePort
```

### Deployment Configuration (flask-deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-library
spec:
  replicas: 1
  # ...other configurations...
```

## License
MIT License

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
