import json

import frappe
from dateutil.relativedelta import relativedelta
from frappe.model.naming import getseries
from frappe.utils import getdate, today


DURATION_FIELDS = ("custom_mce_service_duration", "custom_duration_of_daily_service", "custom_total_length_of_service")


def duration(start, end):
    if not start or not end:
        return ""
    if getdate(end) < getdate(start):
        return ""
    delta = relativedelta(getdate(end), getdate(start))
    return f"{delta.years} سنة، {delta.months} شهر، {delta.days} يوم"


def calculate_durations(doc):
    end = today()
    daily = doc.get("custom_date_of_appointment_as_daily_worker")
    joining = doc.get("date_of_joining")
    doc.custom_mce_service_duration = duration(joining, end)
    doc.custom_duration_of_daily_service = duration(daily, joining)
    doc.custom_total_length_of_service = duration(daily, end) if duration(daily, joining) and duration(joining, end) else ""


def setup_behaviour():
    from masar_mce_hrms.setup import update_custom_field

    with open(frappe.get_app_path("masar_mce_hrms", "employee_select_options.json")) as source:
        options = json.load(source)
    mappings = {"ضباط": "ضابط", "ضباط صف": "ضابط صف"}
    for old, new in mappings.items():
        frappe.db.set_value("Employee", {"custom_group": old}, "custom_group", new, update_modified=False)
    for fieldname, key in (("custom_group", "الفئة"), ("custom_reason_for_leaving_work", "سبب ترك العمل"), ("custom_mce_subunit", "الوحدة الفرعية"), ("custom_mce_service_status", "حالة الموضف")):
        values = options[key]
        # Preserve existing unmapped categories rather than inventing replacements.
        if fieldname == "custom_group":
            existing = frappe.get_all("Employee", fields=[fieldname], distinct=True)
            values = values + sorted({row[fieldname] for row in existing if row[fieldname] and row[fieldname] not in values})
        update_custom_field(fieldname, fieldtype="Select", options="\n" + "\n".join(values))
    for fieldname in DURATION_FIELDS:
        update_custom_field(fieldname, fieldtype="Data", read_only=1)
    sequence = "custom_mce_employee_sequence_number"
    frappe.db.sql(f"UPDATE `tabEmployee` SET `{sequence}` = 0 WHERE `{sequence}` IS NULL OR TRIM(`{sequence}`) = ''")
    name = frappe.db.get_value("Custom Field", {"dt": "Employee", "fieldname": sequence})
    field = frappe.get_doc("Custom Field", name)
    if field.fieldtype != "Int":
        field.flags.ignore_validate = True
        field.fieldtype = "Int"
        field.read_only = 1
        field.save(ignore_permissions=True)
    update_custom_field(sequence, read_only=1)
    maximum = frappe.db.sql(f"SELECT COALESCE(MAX(`{sequence}`), 0) FROM `tabEmployee`")[0][0]
    frappe.db.sql("INSERT INTO `tabSeries` (name,current) VALUES (%s,%s) ON DUPLICATE KEY UPDATE current=GREATEST(current,VALUES(current))", ("MCE-EMPLOYEE-SEQUENCE", maximum))
    for employee in frappe.get_all("Employee", filters={sequence: 0}, pluck="name", order_by="creation asc, name asc"):
        frappe.db.set_value("Employee", employee, sequence, int(getseries("MCE-EMPLOYEE-SEQUENCE", 1)), update_modified=False)
    refresh_durations()


def refresh_durations():
    for row in frappe.get_all("Employee", fields=["name", "date_of_joining", "custom_date_of_appointment_as_daily_worker", *DURATION_FIELDS]):
        old = {field: row[field] for field in DURATION_FIELDS}
        calculate_durations(row)
        values = {field: row[field] for field in DURATION_FIELDS if (old[field] or "") != row[field]}
        if values:
            frappe.db.set_value("Employee", row.name, values, update_modified=False)
