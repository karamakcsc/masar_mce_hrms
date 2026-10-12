"""Preserve the existing Age values while replacing the misspelled field name."""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.model.utils.rename_field import rename_field


def execute():
    if not frappe.db.table_exists("Employee"):
        return
    old = frappe.db.get_value("Custom Field", {"dt": "Employee", "fieldname": "custom_agg"})
    if not old:
        return
    old_field = frappe.get_doc("Custom Field", old)
    if not frappe.db.has_column("Employee", "custom_agg"):
        frappe.throw("Employee Age metadata exists but its custom_agg column is missing. Synchronize the Employee schema before renaming Age.")
    new = frappe.db.get_value("Custom Field", {"dt": "Employee", "fieldname": "custom_age"})
    if new and frappe.db.has_column("Employee", "custom_age"):
        conflicts = frappe.db.sql("SELECT name FROM `tabEmployee` WHERE COALESCE(custom_age,0) <> 0 AND COALESCE(custom_age,0) <> COALESCE(custom_agg,0) LIMIT 1")
        if conflicts:
            frappe.throw("Both Age fields contain different values. Resolve the conflict before migrating; no values have been overwritten.")
    if not new:
        definition = old_field.as_dict()
        for key in ("name", "creation", "modified", "modified_by", "owner", "docstatus", "idx"):
            definition.pop(key, None)
        definition["fieldname"] = "custom_age"
        create_custom_fields({"Employee": [definition]}, update=False)
    rename_field("Employee", "custom_agg", "custom_age")
    for setter in frappe.get_all("Property Setter", filters={"doc_type": "Employee", "property": "field_order"}, fields=["name", "value"]):
        import json
        order = json.loads(setter.value)
        order = list(dict.fromkeys("custom_age" if name == "custom_agg" else name for name in order))
        frappe.db.set_value("Property Setter", setter.name, "value", json.dumps(order), update_modified=False)
    frappe.delete_doc("Custom Field", old, ignore_permissions=True)
    frappe.clear_cache(doctype="Employee")
