# 🛡️ Cyber Response Platform

An AI-powered cybersecurity incident detection and automated response platform designed to identify threats, classify incidents, and execute intelligent response actions in real-time.

---

## 🚀 Overview

This system simulates a real-world **Security Operations Center (SOC)** by combining:

- Machine learning-based detection
- Rule-based classification
- Autonomous response execution
- AI-powered investigation assistant
- Incident reporting and documentation

The platform processes detections, converts them into structured incidents, and automatically decides and executes response actions.

---

## ⚙️ How It Works

The system automatically:

✔ Ingests detection signals  
✔ Classifies incidents using severity rules + ML scoring  
✔ Maps MITRE ATT&CK TTPs  
✔ Predicts kill chain stages  
✔ Assigns autonomy levels (1–4)  
✔ Executes response actions (simulation + real)  
✔ Logs actions and builds investigation timeline  
✔ Allows querying incidents using AI chatbot  
✔ Generates downloadable PDF reports  

---

## 🧠 Core Features

✨ AI-powered incident analysis (LLM-based)  
🛡️ Autonomous response engine (level-based execution)  
📊 Incident classification with explainability (SHAP)  
🧬 MITRE ATT&CK TTP enrichment  
⛓️ Kill chain prediction  
📜 Action audit logging  
🤖 Chat-based investigation interface  
📄 PDF report generation  
🔐 JWT authentication & secure APIs  
⚡ Event-driven architecture (RabbitMQ workers)  

---
## 🧰 Tech Stack / Tools

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Queue-orange)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![Groq](https://img.shields.io/badge/Groq-LLM-purple)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red)

---

---

## 🔐 Authentication

- JWT-based authentication
- Secure endpoints:
  - Chat API
  - PDF generation
  - Incident access

---

## 📡 API Endpoints

### 🔹 Auth
POST /api/v1/auth/signup
POST /api/v1/auth/login

### 🔹 Incidents
GET /api/v1/incidents/
GET /api/v1/incidents/{id}
GET /api/v1/incidents/{id}/timeline

### 🔹 AI Chat
GET /api/v1/chat/{incident_id}?question=...

### 🔹 PDF Report
GET /api/v1/incidents/{id}/report


---

## 🤖 AI Chat Example

Ask questions like:

- "Explain this incident"
- "What actions were taken?"
- "What is the risk level?"
- "How to mitigate this attack?"

---

## 📄 PDF Report

Generates a complete report including:

- Incident details
- Severity and risk
- TTPs and kill chain
- Actions taken
- Suggested mitigation

---

## ⚡ Autonomous Response Levels

| Level | Behavior |
|-------|--------|
|   1   | Alert only |
|   2   | Suggest actions |
|   3   | Partial automation |
|   4   | Full autonomous response |

---
### 🧠 Future Improvements
Role-based access control (RBAC)
Real SIEM integration
Threat intelligence feeds
Dashboard UI (React)
Multi-tenant support

### 👨‍💻 Author
Daksh Verma
