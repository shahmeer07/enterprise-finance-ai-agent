def tool_get_overdue_invoices(input: str):
    invoices = get_overdue_invoices(minimum_days_overdue=15, limit=10)
    log_action("FETCH_INVOICES", {"count": len(invoices)})
    return invoices


def tool_analyze_invoice_risk(invoices):
    risks = analyze_invoice_risk(invoices)
    log_action("ANALYZE_RISK", risks)
    return risks


def draft_followup_email(invoice):
    subject = (
        f"Overdue Invoice Reminder – {invoice['invoice_id']} "
        f"({invoice['days_overdue']} days overdue)"
    )

    body = f"""
Dear {invoice.get('customer', 'Finance Team')},

This is a reminder regarding the following overdue invoice:

Invoice ID: {invoice['invoice_id']}
Amount: {invoice['total_amount']}
Days Overdue: {invoice['days_overdue']}

We kindly request that you review and process the outstanding payment
at your earliest convenience.

If the invoice is under dispute, please let us know.

Best regards,

Sent by AI Agent
© Muhammad Shahmeer Khan
""".strip()

    return {
        "subject": subject,
        "body": body
    }
