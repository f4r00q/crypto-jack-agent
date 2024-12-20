# eBPF Monitor: Kubernetes Security and Adversary Detection Tool

## **Overview**
The `eBPF Monitor` is a Kubernetes security tool that detects adversarial behavior in containers and Pods. It leverages eBPF for system call monitoring, Kubernetes metadata enrichment, and machine learning-based anomaly detection.

### **Key Features**
- **eBPF Monitoring**: Tracks system calls (`curl`, `wget`, `ssh`, `docker`) in real-time.
- **Kubernetes Metadata Enrichment**: Maps suspicious activities to Pods and Namespaces.
- **Anomaly Detection**: Uses Isolation Forest ML models.
- **Alerting System**: Sends email notifications and logs critical events.
- **Prometheus Metrics Exporter**: Integrates with Grafana for visual monitoring.

---

## **Project Structure**
```
.
├── ebpf_monitor/                # Main application package
│   ├── app.py                  # Flask API and endpoints
│   ├── ebpf_monitor.py         # eBPF monitoring core
│   ├── database.py             # PostgreSQL interaction
│   ├── authentication.py       # JWT-based authentication
│   ├── email_alert.py          # Email alerting system
│   ├── config.py               # Configuration management
│   ├── prometheus.py           # Prometheus metrics exporter
│   ├── enricher.py             # Kubernetes metadata enrichment
│   ├── simulation.py           # Adversary action simulation
├── tests/                      # Unit and integration tests
│   ├── kubernetes/             # Kubernetes testing files
│   │   └── adversary-simulation.yaml
│   ├── test_database.py        # Database tests
│   ├── test_authentication.py  # Authentication tests
│   ├── test_email_alert.py     # Email alert tests
│   ├── test_integration.py     # Integration tests
│   ├── test_simulation.py      # Simulation tests
├── deployments/                # Deployment files
│   ├── Dockerfile              # Docker container definition
│   ├── docker-compose.yml      # Docker Compose setup
│   ├── deployment.yaml         # Kubernetes deployment
├── .github/                    # GitHub CI/CD configurations
│   └── workflows/ci.yml        # CI pipeline configuration
├── scripts/                    # Utility scripts
│   └── init_db.sh              # DB initialization script
├── pyproject.toml              # Poetry dependency file
├── run.py                      # CLI entry point
└── README.md                   # Project documentation
```

---

## **Installation Instructions**

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd ebpf_monitor
```

### **2. Install Dependencies with Poetry**
```bash
poetry install
```

### **3. Initialize the Database**
```bash
poetry run python run.py --init-db
```

### **4. Start the Application**
```bash
poetry run python run.py --start
```

### **5. Simulate Adversarial Actions** (Testing Only)
```bash
poetry run python run.py --simulate
```

---

## **Deployment Instructions**

### **Local Deployment (Docker)**
```bash
docker-compose up --build
```

### **Kubernetes Deployment**
```bash
# Build Docker image
docker build -t ebpf-monitor:latest .

# Apply Kubernetes Manifests
kubectl apply -f deployments/deployment.yaml
```

---

## **Testing the Application**
### **Run All Tests**
```bash
poetry run pytest tests/
```

### **Kubernetes Testing Simulation**
```bash
kubectl apply -f tests/kubernetes/adversary-simulation.yaml
```

---

## **Accessing the Services**
- **Flask API**: `http://localhost:5000`
- **Prometheus Metrics**: `http://localhost:8000/metrics`

---

## **Environment Variables**
```env
SECRET_KEY=supersecretkey
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
EMAIL_SENDER=alert@example.com
EMAIL_RECIPIENT=recipient@example.com
SMTP_USER=user
SMTP_PASSWORD=password
```

---

## **Contributing**
1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a pull request.

---

## **License**
MIT License

---

## **Contact**
For issues or contributions, create an issue or pull request on GitHub.
