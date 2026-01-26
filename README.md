# SwitchLang 🔄

**SwitchLang** is an AI-powered language learning assistant designed to practice "Active Recall." It allows users to switch between input and output languages dynamically, providing real-time feedback using Google's Gemini LLM.

This project demonstrates a full **DevOps lifecycle**, featuring a microservices architecture deployed on Kubernetes using IaC and GitOps practices.

## 🚀 Key Features
- **Dynamic Language Switching**: Convert input from any language to target language exercises.
- **AI-Powered Feedback**: Instantly corrects grammar and nuances using **Google Gemini 1.5 API**.
- **Active Recall**: Generates lists of sentences for translation practice based on daily inputs.
- **Interactive UI**: Built with Streamlit for a responsive and simple user experience.

## 🛠 Tech Stack

### Application
- **Language**: Python 3.11+
- **Frontend**: Streamlit
- **AI Integration**: **Google Generative AI SDK (Gemini 1.5 Flash)**

### Infrastructure & DevOps
- **Containerization**: Docker (Multi-stage builds)
- **Orchestration**: Kubernetes (Kind for local development)
- **IaC**: Terraform
- **CI/CD**: GitHub Actions, ArgoCD
- **Ingress**: Nginx Ingress Controller

## 📂 Project Structure
```bash
switchlang/
├── .github/      # CI workflows
├── app/          # Source code (Python + Streamlit)
├── infra/        # Terraform configurations (Infrastructure provisioning)
└── k8s/          # Kubernetes manifests & Helm charts