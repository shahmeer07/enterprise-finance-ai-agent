# agent/orchestrator.py

import json
import re
import math
from datetime import date, datetime
from decimal import Decimal
from dotenv import load_dotenv
from openai import OpenAI

from tools.gmail_sender import send_email_via_gmail
from tools.invoice import get_overdue_invoices
from tools.customer import get_customer_email
from tools.risk import analyze_invoice_risk
from tools.drafting import draft_followup_email
from tools.audit import log_action

load_dotenv()
client = OpenAI()

# ------------------------
# Function definitions added for LLM visibility, ultimately calling our tools defined.
# ------------------------
functions = [
    {
        "name": "get_overdue_invoices",
        "description": "Fetch overdue invoices from the ERP system",
        "parameters": {
            "type": "object",
            "properties": {
                "minimum_days_overdue": {"type": "integer"},
                "limit": {"type": "integer"},
            },
            "required": ["minimum_days_overdue", "limit"],
        },
    },
    {
        "name": "analyze_invoice_risk",
        "description": "Analyze risk level of overdue invoices",
        "parameters": {
            "type": "object",
            "properties": {
                "invoices": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {"type": "string"},
                            "customer_id": {"type": "string"},
                            "days_overdue": {"type": "integer"},
                            "amount": {"type": "number"},
                        },
                        "required": [
                            "invoice_id",
                            "customer_id",
                            "days_overdue",
                            "amount",
                        ],
                    },
                }
            },
            "required": ["invoices"],
        },
    },
]

SYSTEM_PROMPT = """
You are an enterprise finance operations agent.

Rules:
- Do not invent data.
- Only call functions when needed.
- Never send/draft emails without explicit user approval.
- If the user asks for non-overdue invoices, do NOT call any function.
- If the user requests overdue invoices but does not specify a limit,
  default to returning the top 10 overdue invoices.
- Be concise, factual, and deterministic.
"""

MAX_STEPS = 3

# ------------------------
# Session state , making sure our session persist and state doesnt change immediately 
# ------------------------
session_state = {
    "last_invoices": None,
    "last_risk_analysis": None,
    "pending_action": None,   # e.g. "send_email_via_gmail"
    "pending_payload": None,  # list of {"invoice": inv, "email": {"subject":..,"body":..}}
}

# ------------------------
# Helper: make objects JSON-safe (for pandas Timestamp / numpy types / NaN etc)
# ------------------------
try:
    import numpy as np  # optional
except Exception:
    np = None

try:
    from pandas import Timestamp  # optional
except Exception:
    Timestamp = None


def make_json_safe(obj):
    if obj is None:
        return None

    if isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(x) for x in obj]
    if isinstance(obj, tuple):
        return [make_json_safe(x) for x in obj]

    if Timestamp is not None and isinstance(obj, Timestamp):
        return obj.isoformat()

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if np is not None:
        try:
            if isinstance(obj, np.generic):
                obj = obj.item()
        except Exception:
            pass

    if isinstance(obj, Decimal):
        return float(obj)

    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if hasattr(obj, "isoformat") and callable(getattr(obj, "isoformat")):
        try:
            return obj.isoformat()
        except Exception:
            pass

    return obj


def dumps_json_safe(obj) -> str:
    return json.dumps(make_json_safe(obj), ensure_ascii=False)


# ------------------------
# Helper: enrich invoices with customer email
# ------------------------
def enrich_with_customer_data(invoices):
    for inv in invoices:
        customer_id = inv.get("customer_id")
        inv["customer_email"] = get_customer_email(customer_id) if customer_id else None
    return invoices


# ------------------------
# Helper: build previews + store pending send payload
# ------------------------
TEST_TO_EMAIL = "shahmeerk3000@gmail.com"


def build_email_previews_and_arm_send(invoices):
    payload = []
    previews = []

    for inv in invoices:
        email = draft_followup_email(inv)  # must return {"subject":..., "body":...}

        payload.append({"invoice": inv, "email": email})

        previews.append(
            f"---\n"
            f"Invoice: {inv.get('invoice_id','UNKNOWN')}\n"
            f"To (TEST): {TEST_TO_EMAIL}\n"
            f"Subject: {email.get('subject','')}\n"
            f"Body:\n{email.get('body','')}\n"
        )

    session_state["pending_action"] = "send_email_via_gmail"
    session_state["pending_payload"] = payload

    return "\n".join(previews)


# ------------------------
# Agent entry point
# ------------------------
def run_agent(user_input: str):
    user_lower = user_input.lower().strip()

    wants_email_flow = any(
        phrase in user_lower for phrase in ["draft", "email", "send", "notify", "remind"]
    )

    # --------------------------------------------------
    # DRAFT INTENT HANDLING (ARM ACTION FIRST)
    # --------------------------------------------------
    if wants_email_flow and session_state["last_invoices"]:
        invoice_ids = re.findall(r"INV-\d+", user_input.upper())

        selected = [
            inv for inv in session_state["last_invoices"]
            if inv.get("invoice_id") in invoice_ids
        ]

        if not selected:
            return "Please specify which invoice(s) you want to draft the email for."

        previews = build_email_previews_and_arm_send(selected)

        return (
            "Follow-up Email Preview (TEST MODE)\n\n"
            f"{previews}\n\n"
            "Do you approve sending this email? (yes/no)"
        )


    # --------------------------------------------------
    # 1) HUMAN APPROVAL GATE (ONLY sends if we previously armed a pending action)
    # --------------------------------------------------
    if user_lower in ["yes", "y"] and session_state["pending_action"] == "send_email_via_gmail":
        payload = session_state["pending_payload"] or []
        results = []

        for item in payload:
            inv = item["invoice"]
            email = item["email"]

            # SEND (TEST) via Gmail
            send_email_via_gmail(
                to_email=TEST_TO_EMAIL,
                subject=email.get("subject", ""),
                body=email.get("body", ""),
            )

            log_action("EMAIL_SENT", {"invoice_id": inv.get("invoice_id"), "to": TEST_TO_EMAIL})
            results.append(f"✅ Email sent for invoice {inv.get('invoice_id','UNKNOWN')}")

        # clear pending state
        session_state["pending_action"] = None
        session_state["pending_payload"] = None

        return "\n".join(results) if results else "Nothing to send."

    if user_lower in ["no", "n"] and session_state["pending_action"]:
        # user declined the pending action
        payload = session_state["pending_payload"] or []
        for item in payload:
            inv = item.get("invoice", {})
            log_action("EMAIL_SEND_REJECTED", {"invoice_id": inv.get("invoice_id")})

        session_state["pending_action"] = None
        session_state["pending_payload"] = None
        return "Action cancelled. No emails were sent."

    # --------------------------------------------------
    # 2) If user asks to email "these/those invoices" but no IDs provided
    # --------------------------------------------------
    context_phrases = [
        "the invoices you just",
        "the invoices you gave me",
        "these invoices",
        "those invoices",
        "all of these invoices",
        "all the invoices you gave me",
    ]

    if any(p in user_lower for p in context_phrases) and wants_email_flow:
        if not session_state["last_invoices"]:
            return "I don’t have any invoices from this session yet. Please list overdue invoices first."

        return (
            "Which invoice IDs should I email about?\n\n"
            "Available in this session:\n- "
            + "\n- ".join(inv.get("invoice_id", "UNKNOWN") for inv in session_state["last_invoices"])
        )

    # --------------------------------------------------
    # 3) "all of them" selection (generate preview + ask approval)
    # --------------------------------------------------
    if "all of them" in user_lower and session_state["last_invoices"] and wants_email_flow:
        previews = build_email_previews_and_arm_send(session_state["last_invoices"])
        return (
            "Follow-up Email Preview(s) (TEST MODE)\n\n"
            f"{previews}\n\n"
            "Do you approve sending these emails now? (yes/no)"
        )

    # --------------------------------------------------
    # 4) Selection by invoice IDs (generate preview + ask approval)
    # --------------------------------------------------
    invoice_ids = re.findall(r"INV-\d+", user_input.upper())
    if invoice_ids and session_state["last_invoices"] and wants_email_flow:
        selected = [
            inv for inv in session_state["last_invoices"]
            if inv.get("invoice_id") in invoice_ids
        ]

        if not selected:
            return "I couldn’t find those invoice IDs in the current list. Please request overdue invoices again."

        previews = build_email_previews_and_arm_send(selected)
        return (
            "Follow-up Email Preview(s) (TEST MODE)\n\n"
            f"{previews}\n\n"
            "Do you approve sending these emails now? (yes/no)"
        )

    # --------------------------------------------------
    # 5) LLM reasoning loop (fetch invoices, analyze risk, etc.)
    # --------------------------------------------------
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for _ in range(MAX_STEPS):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=functions,
            function_call="auto",
            max_tokens=400,
        )

        message = response.choices[0].message

        # function call
        if getattr(message, "function_call", None):
            name = message.function_call.name
            args = json.loads(message.function_call.arguments)

            if name == "get_overdue_invoices":
                invoices = get_overdue_invoices(**args)
                invoices = enrich_with_customer_data(invoices)

                session_state["last_invoices"] = invoices
                log_action("FETCH_INVOICES", {"count": len(invoices)})

                messages.append(message)
                messages.append(
                    {
                        "role": "function",
                        "name": name,
                        "content": dumps_json_safe(invoices),
                    }
                )
                continue

            if name == "analyze_invoice_risk":
                risks = analyze_invoice_risk(args["invoices"])
                session_state["last_risk_analysis"] = risks
                log_action("ANALYZE_RISK", risks)

                messages.append(message)
                messages.append(
                    {
                        "role": "function",
                        "name": name,
                        "content": dumps_json_safe(risks),
                    }
                )
                continue

        # no function call: return assistant content
        return message.content

    return "Unable to complete the request within safe execution limits."
