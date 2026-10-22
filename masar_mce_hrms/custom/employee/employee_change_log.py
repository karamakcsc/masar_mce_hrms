import frappe
from frappe import _
from frappe.utils import add_days, cint, cstr, formatdate, get_datetime, getdate, now_datetime


DECISION_LOG_FIELDS = [
    "custom_is_seconded",
    "custom_seconded_from",
    "custom_seconded_to",
    "custom_secondment_date",
    "custom_secondment_letter_number",
    "custom_transfer_date_to_institution",
    "custom_secondment_end_date",
    "custom_is_staff_officer",
    "custom_appointed_position",
    "custom_rank_upon_appointment",
]

SERVICE_INTERRUPTION_LOG_FIELDS = [
    "custom_termination_date",
    "custom_termination_letter_number",
    "custom_reinstatement_date",
    "custom_reinstatement_letter_number",
    "custom_total_suspension_duration",
    "custom_remarks",
]

LOG_GROUPS = {
    "Employee Decision Log": DECISION_LOG_FIELDS,
    "Employee Service Interruption Log": SERVICE_INTERRUPTION_LOG_FIELDS,
}


def create_change_logs(doc):
    previous = doc.get_doc_before_save()
    if not previous:
        return
    timestamp = now_datetime()
    for log_doctype, fieldnames in LOG_GROUPS.items():
        changes = get_changed_fields(doc, previous, fieldnames)
        if not changes:
            continue
        frappe.get_doc({
            "doctype": log_doctype,
            "employee": doc.name,
            "employee_name": doc.employee_name,
            "changed_by": frappe.session.user,
            "modification_timestamp": timestamp,
            "changes": changes,
        }).insert(ignore_permissions=True)


def get_changed_fields(doc, previous, fieldnames):
    changes = []
    for fieldname in fieldnames:
        df = doc.meta.get_field(fieldname)
        if not df:
            continue
        old_value = normalize_value(previous.get(fieldname), df.fieldtype)
        new_value = normalize_value(doc.get(fieldname), df.fieldtype)
        if old_value == new_value:
            continue
        changes.append({
            "field_label": df.label,
            "field_name": fieldname,
            "field_type": df.fieldtype,
            "old_value": old_value,
            "new_value": new_value,
        })
    return changes


def normalize_value(value, fieldtype):
    if fieldtype == "Check":
        return cstr(cint(value))
    if fieldtype == "Date":
        return cstr(getdate(value)) if value else ""
    return cstr(value)


def get_change_log_report(log_doctype, filters):
    filters = frappe._dict(filters or {})
    return get_report_columns(log_doctype), get_report_data(log_doctype, filters)


def get_report_columns(log_doctype):
    return [
        {"fieldname": "modification_timestamp", "label": _("Timestamp"), "fieldtype": "Datetime", "width": 170},
        {"fieldname": "log", "label": _("Log"), "fieldtype": "Link", "options": log_doctype, "width": 140},
        {"fieldname": "employee", "label": _("Employee"), "fieldtype": "Link", "options": "Employee", "width": 130},
        {"fieldname": "employee_name", "label": _("Employee Name"), "fieldtype": "Data", "width": 200},
        {"fieldname": "field_label", "label": _("Field"), "fieldtype": "Data", "width": 200},
        {"fieldname": "old_value", "label": _("Old Value"), "fieldtype": "Data", "width": 180},
        {"fieldname": "new_value", "label": _("New Value"), "fieldtype": "Data", "width": 180},
        {"fieldname": "changed_by", "label": _("Modified By"), "fieldtype": "Link", "options": "User", "width": 180},
    ]


def get_report_data(log_doctype, filters):
    log = frappe.qb.DocType(log_doctype)
    detail = frappe.qb.DocType("Employee Change Log Detail")
    query = (
        frappe.qb.from_(log)
        .inner_join(detail).on((detail.parent == log.name) & (detail.parenttype == log_doctype))
        .select(
            log.name.as_("log"),
            log.modification_timestamp,
            log.employee,
            log.employee_name,
            log.changed_by,
            detail.field_label,
            detail.field_type,
            detail.old_value,
            detail.new_value,
        )
        .orderby(log.modification_timestamp, order=frappe.qb.desc)
        .orderby(log.name, order=frappe.qb.desc)
        .orderby(detail.idx)
    )
    if filters.employee:
        query = query.where(log.employee == filters.employee)
    if filters.changed_by:
        query = query.where(log.changed_by == filters.changed_by)
    if filters.from_date:
        query = query.where(log.modification_timestamp >= get_datetime(filters.from_date))
    if filters.to_date:
        query = query.where(log.modification_timestamp < get_datetime(add_days(filters.to_date, 1)))

    data = query.run(as_dict=True)
    for row in data:
        row.field_label = _(row.field_label)
        row.old_value = format_log_value(row.old_value, row.field_type)
        row.new_value = format_log_value(row.new_value, row.field_type)
    return data


def format_log_value(value, fieldtype):
    if fieldtype == "Check":
        return _("Yes") if cint(value) else _("No")
    if fieldtype == "Date" and value:
        return formatdate(value)
    return value or ""
