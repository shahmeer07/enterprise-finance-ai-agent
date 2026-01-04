# Tool Execution Layer

## Purpose
The tools module contains **deterministic, auditable functions** that the agent can invoke.

The LLM never accesses data directly — it interacts exclusively through these tools.

---

## Available Tools

### invoice.py – get_overdue_invoices
Fetches overdue invoice data from the data layer.
(Currently uses dummy JSON data; designed for ERP API replacement.)

---

### risk.py – analyze_invoice_risk
Evaluates invoice severity using:
- Days overdue
- Invoice amount
- Customer tier

Returns prioritized risk classifications.

---

### drafting.py – draft_followup_email
Generates professional follow-up email drafts.
This tool does NOT send emails.

---

### audit.py – log_action
Writes agent actions to an append-only audit log.
Supports traceability and compliance.

---

## Safety Model
- Tools are read-only where applicable
- No irreversible actions are permitted
- All tool invocations are logged
- Execution logic is isolated from reasoning

This design ensures enterprise-grade reliability and control.
