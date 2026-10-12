import frappe


AUTOMATIC_LOG_TOKEN = object()
SHARED_FIELDS = {
    "category": "custom_group",
    "employee_number": "employee_number",
    "employee_name": "employee_name",
    "notes": "custom_mce_notes",
}
LOG_DOCTYPES = ("Employee Administrative Letter Log", "Employee Leave Log")


def capture_employee_changes(doc, method=None):
    previous = doc.get_doc_before_save()
    if previous is None:
        return
    if not any(doc.get(source) != previous.get(source) for source in SHARED_FIELDS.values()):
        return
    for doctype in LOG_DOCTYPES:
        log = frappe.get_doc({
            "doctype": doctype,
            "employee": doc.name,
            **{target: doc.get(source) for target, source in SHARED_FIELDS.items()},
        })
        log.flags.mce_log_token = AUTOMATIC_LOG_TOKEN
        log.insert(ignore_permissions=True)
