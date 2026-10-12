import json

import frappe
from masar_mce_hrms.services.service_duration import DURATION_FIELDS


def setup_behaviour():
    from masar_mce_hrms.customization.setup import update_custom_field

    with open(frappe.get_app_path("masar_mce_hrms", "configuration", "employee_select_options.json")) as source:
        options = json.load(source)
    for fieldname, key in (("custom_group", "الفئة"), ("custom_reason_for_leaving_work", "سبب ترك العمل"), ("custom_mce_subunit", "الوحدة الفرعية"), ("custom_mce_service_status", "حالة الموضف")):
        values = options[key]
        # Preserve existing unmapped categories rather than inventing replacements.
        if fieldname == "custom_group":
            existing = frappe.get_all("Employee", fields=[fieldname], distinct=True)
            values = values + sorted({row[fieldname] for row in existing if row[fieldname] and row[fieldname] not in values})
        update_custom_field(fieldname, fieldtype="Select", options="\n" + "\n".join(values))
    for fieldname in DURATION_FIELDS:
        update_custom_field(fieldname, fieldtype="Data", read_only=1)
    update_custom_field("custom_mce_employee_sequence_number", read_only=1)
