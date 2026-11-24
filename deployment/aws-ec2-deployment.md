# AWS EC2 Production Deployment Guide

This guide details the complete, production-grade deployment process for the **Subscription Renewal and Expense Analytics Platform** on **Amazon Web Services (AWS) Elastic Compute Cloud (EC2)**.

---

## 1. Cloud Architecture & Provisioning Sizing

```mermaid
flowchart TD
    Client(["Internet Clients (Browsers)"]) -->|HTTPS 443| ALB["Nginx / ALB Reverse Proxy"]
    subgraph VPC ["AWS Virtual Private Cloud (VPC) 10.0.0.0/16"]
        subgraph PublicSubnet ["Public Subnet (10.0.1.0/24)"]
            ALB
        end
        subgraph EC2Host ["EC2 Host (t3.medium - Ubuntu 24.04 LTS)"]
            subgraph DockerCompose ["Docker Compose Mesh (Bridge Network)"]
                Frontend["Angular Frontend (Port 4200/80)"]
                Backend["FastAPI Core Backend (Port 8000)"]
                Analytics["Flask Analytics Service (Port 5001)"]
                MySQL[("MySQL 8.0 (Port 3306)")]
                Redis[("Redis 7 (Port 6379)")]
                Prometheus["Prometheus (Port 9090)"]
                Grafana["Grafana (Port 3000)"]
                FAISS[("FAISS Vector Index")]
            end
        end
        subgraph AWSStorage ["AWS Managed Storage"]
            S3["Amazon S3 (Encrypted Backups)"]
            EBS["EBS gp3 50GB Volume"]
        end
    end

    ALB -->|Proxy| Frontend
    ALB -->|/api/| Backend
    Backend <-->|SQL Queries| MySQL
    Backend <-->|Cache & Limits| Redis
    Backend <-->|Internal HTTP| Analytics
    Backend <-->|Vector Retrieval| FAISS
    Prometheus -->|Scrape| Backend
    Prometheus -->|Scrape| Analytics
    Grafana -->|Query| Prometheus
    EC2Host -->|Daily Dump| S3
    DockerCompose -->|Mounts| EBS
```

### Recommended EC2 Specifications

| Component | Minimum Specification | Recommended Production |
| :--- | :--- | :--- |
| **Instance Type** | `t3.medium` (2 vCPU, 4 GiB RAM) | `t3.large` or `c6i.large` (2 vCPU, 4-8 GiB RAM) |
| **Root Volume** | 30 GB EBS gp3 (3,000 IOPS, 125 MB/s) | 50 GB EBS gp3 |
| **Operating System**| Ubuntu Server 24.04 LTS (HVM) | Ubuntu Server 24.04 LTS (HVM) |
| **Elastic IP** | 1 Elastic IP (Static Public IPv4) | 1 Elastic IP |

---

## 2. AWS Security Group Rules

Create a dedicated Security Group: `sg-subscription-tracker-prod`.

| Type | Protocol | Port Range | Source | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **SSH** | TCP | `22` | `<Your-Corporate-IP>/32` | Bastion / Secure administration only |
| **HTTP** | TCP | `80` | `0.0.0.0/0` | Let's Encrypt validation & HTTPS redirect |
| **HTTPS** | TCP | `443` | `0.0.0.0/0` | Production end-user traffic |
| **All Other Ports** | ALL | ALL | Denied (Internal Only)| MySQL, Redis, FastAPI, Prometheus, Grafana are kept off the public internet |

---

## 3. Host Preparation & Docker Setup

Connect to your EC2 instance via SSH:

```bash
ssh -i ~/.ssh/id_rsa_aws ubuntu@<EC2-ELASTIC-IP>
```

Update system packages and enable security upgrades:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg lsb-release git ufw fail2ban

# Configure UFW Firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Install the official Docker Engine and Docker Compose plugin:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow ubuntu user to execute docker without sudo
sudo usermod -aG docker ubuntu
newgrp docker
```

Configure a 4GB Swap file to prevent Out-Of-Memory (OOM) incidents during peak bursts:

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 4. Application Cloning and Configuration

Clone the repository into `/opt/subscription-tracker`:

```bash
sudo mkdir -p /opt/subscription-tracker
sudo chown ubuntu:ubuntu /opt/subscription-tracker
git clone https://github.com/harsharaju1314-hash/Subscription-Renewal-and-Expense-Tracker.git /opt/subscription-tracker
cd /opt/subscription-tracker
```

Create the production `.env` file:

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

Ensure the following variables are securely populated:

```env
ENVIRONMENT=production
DEBUG=False
PROJECT_NAME="Subscription Renewal & Expense Analytics Platform"
VERSION=1.0.0

# Security Secrets (Must be at least 32 characters)
SECRET_KEY=YOUR_SECURE_RANDOMLY_GENERATED_JWT_SECRET_KEY_32_CHARS
INTERNAL_SERVICE_SECRET=YOUR_SECURE_INTERNAL_MICROSERVICE_SECRET_32_CHARS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MySQL Production Credentials
MYSQL_ROOT_PASSWORD=SUPER_SECURE_MYSQL_ROOT_PASSWORD_2026
MYSQL_DATABASE=subscription_db
MYSQL_USER=sub_user
MYSQL_PASSWORD=SUPER_SECURE_MYSQL_USER_PASSWORD_2026
DATABASE_URL=mysql+pymysql://sub_user:SUPER_SECURE_MYSQL_USER_PASSWORD_2026@mysql:3306/subscription_db

# Redis
REDIS_PASSWORD=SUPER_SECURE_REDIS_PASSWORD_2026
REDIS_URL=redis://:SUPER_SECURE_REDIS_PASSWORD_2026@redis:6379/0

# Microservices
ANALYTICS_SERVICE_URL=http://analytics-service:5001

# Artificial Intelligence (OpenAI & LangChain)
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_OPENAI_API_KEY
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
FAISS_INDEX_DIR=/app/data/faiss_index

# Monitoring
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=SUPER_SECURE_GRAFANA_PASSWORD_2026
```

---

## 5. SSL Certificate Acquisition (Let's Encrypt)

Install Certbot and obtain an SSL certificate:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

Set up automatic renewal:

```bash
sudo systemctl enable certbot.timer
```

---

## 6. Deploy Services via Docker Compose

Build and launch all services in detached mode:

```bash
docker compose up -d --build
```

Verify service status:

```bash
docker compose ps
```

Seed initial synthetic data (1,050 records):

```bash
docker compose exec backend python -m database.seeds.generate_synthetic_data
```

Verify liveness and readiness healthchecks:

```bash
curl -I http://localhost:8000/health/live
curl -s http://localhost:8000/health/ready | jq .
```

---

## 7. Automated Backups & Systemd Service

Make scripts executable:

```bash
chmod +x deployment/backup.sh deployment/rollback.sh
```

Configure daily automated backups using `cron`:

```bash
sudo crontab -e
```

Add the following entry to trigger daily at 02:00 UTC:

```cron
0 2 * * * /opt/subscription-tracker/deployment/backup.sh >> /var/log/subtrack-backup.log 2>&1
```

Create a systemd service to auto-start Docker Compose on server reboot:

```ini
# /etc/systemd/system/subscription-tracker.service
[Unit]
Description=Subscription Platform Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/subscription-tracker
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable subscription-tracker.service
```

---

## 8. Rollback Procedure

To roll back to a prior commit or Docker tag during an incident:

```bash
cd /opt/subscription-tracker
./deployment/rollback.sh <PREVIOUS_COMMIT_OR_TAG> [<BACKUP_TIMESTAMP>]
```

Example:

```bash
./deployment/rollback.sh v1.0.0 20261124_020000
```
