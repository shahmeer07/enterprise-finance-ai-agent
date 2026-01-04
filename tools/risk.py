# tools/risk.py

def analyze_invoice_risk(invoices):
    results = []

    for inv in invoices:
        risk = "Low"

        if inv["days_overdue"] > 45 or inv["amount"] > 4000:
            risk = "High"
        elif inv["days_overdue"] > 20:
            risk = "Medium"

        results.append({
            "invoice_id": inv["invoice_id"],
            "customer": inv["customer"],
            "days_overdue": inv["days_overdue"],
            "amount": inv["amount"],
            "risk_level": risk
        })

    return results
