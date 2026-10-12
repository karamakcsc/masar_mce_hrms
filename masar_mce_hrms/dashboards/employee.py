def employee_dashboard(data):
    logs = ["Employee Administrative Letter Log", "Employee Leave Log"]
    transactions = data.setdefault("transactions", [])
    existing = {item for group in transactions for item in group.get("items", [])}
    missing = [log for log in logs if log not in existing]
    if missing:
        transactions.append({"label": "Historical Logs", "items": missing})
    data.setdefault("non_standard_fieldnames", {}).update({log: "employee" for log in logs})
    return data
