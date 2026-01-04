# Agentic Overdue Invoice Assistant

An **agentic AI system** designed for finance and accounts receivable teams to manage overdue invoices using natural language, human-in-the-loop approvals, and external tool execution.

This project demonstrates how to build a **real-world AI agent** that:
- Reasons over structured financial data
- Maintains conversational and operational state
- Requires explicit human approval before taking action
- Integrates securely with external systems (Gmail API via OAuth)

---

## 🚀 What This Agent Does

The agent supports end-to-end overdue invoice workflows:

- 📊 **Retrieve overdue invoices** from structured datasets (Excel / ERP-style data)
- ⚠️ **Assess invoice risk** based on days overdue
- ✉️ **Generate AI-written follow-up emails** (subject + body)
- 🧠 **Enforce human approval** before any email is sent
- 📧 **Send emails via Gmail API** using OAuth authentication
- 📝 **Audit all actions** for traceability

This is an **agentic system** that reasons, plans, pauses for approval, and then executes actions.

---
## Problem Statement

Overdue invoice follow-ups are typically manual, inconsistent, and error-prone.
This agent demonstrates how AI systems can safely automate financial workflows
while preserving human control, auditability, and compliance.
---
## 🧠 Architecture Overview

User
↓
CLI Interface (main.py)
↓
Agent Orchestrator
├── Reasoning (LLM)
├── State Management
├── Approval Gates
└── Tool Invocation
├── Invoice Data Tool
├── Risk Analysis Tool
├── Email Drafting Tool
└── Gmail Sender Tool (OAuth)


Key design principles:
- **Human-in-the-loop safety**
- **Deterministic business rules**
- **Tool-based execution**
- **No hallucinated data**

---

## 🛡️ Safety & Governance

This agent enforces:
- ✅ Explicit approval before sending any email
- ✅ No data invention (only uses source datasets)
- ✅ Clear audit logging
- ✅ Test-mode email sending (safe by default)

This mirrors how AI agents are expected to operate in **regulated enterprise environments**.

---


---

## ⚙️ Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/agentic-overdue-invoice-assistant.git
cd agentic-overdue-invoice-assistant

```

### 2️⃣ Set Up Environment
conda create -n invoice-agent python=3.10
conda activate invoice-agent
pip install -r requirements.txt

### 3️⃣ Configure Environment Variables
OPENAI_API_KEY=your_openai_key_here
GMAIL_CLIENT_ID=your_google_client_id
GMAIL_CLIENT_SECRET=your_google_client_secret

### 4️⃣ Run the Agent
python main.py

## Example Interaction:

You: give me top 5 overdue invoices
You: draft email for INV-5076
Agent: (shows email preview)
Agent: Do you approve sending this email? (yes/no)


## ✉️ Gmail Integration Notes

Uses Google OAuth 2.0

App runs in testing mode by default

Only approved test accounts can send emails

Production deployment would require Google verification or service accounts


## This repository demonstrates:

Practical agentic AI patterns

Real-world human approval gates

Enterprise-style tool orchestration

Secure external system integration

These are the same architectural patterns used in:

Enterprise copilots

Finance automation platforms

Internal AI operations tools

## Non-Goals

This project intentionally does not:
- Fully automate financial actions without human approval
- Modify financial records directly
- Replace accounting or legal judgment

The focus is safe automation with human oversight.

---

## 👤 Author

Muhammad Shahmeer Khan

This project is part of ongoing work in applied AI, automation, and enterprise system integration.

📜 License

MIT License
