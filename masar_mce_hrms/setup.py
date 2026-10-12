import json

import frappe
from decimal import Decimal, InvalidOperation
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def employee_fields():
    definitions = [
        ("service_details_tab", "Additional Service Details", "Tab Break"),
        ("personal_service_section", "Personal and Service", "Section Break"),
        ("place_of_birth", "Place of Birth", "Data"),
        ("employee_sequence_number", "Employee Sequence Number", "Data"),
        ("department", "Department", "Data"),
        ("service_status", "Employee Service Status", "Select"),
        ("education_level", "Education Level", "Data"),
        ("alternative_phone_number", "Alternative Phone Number", "Data"),
        ("enlistment_date", "Enlistment Date", "Date"),
        ("last_promotion_date", "Promotion Date to Current Rank", "Date"),
        ("appointment_certificate_number", "Appointment Certificate Number", "Data"),
        ("subunit", "Subunit", "Data"),
        ("employment_type", "Employment Type", "Data"),
        ("service_duration", "Service Duration", "Small Text"),
        ("service_reinstatement_date", "Service Reinstatement Date", "Date"),
        ("decisions_attachments_section", "Decisions and Attachments", "Section Break"),
        ("release_letter_number", "Termination Letter Number", "Data"),
        ("release_date", "Termination Date", "Date"),
        ("attachment_letter_number", "Attachment Letter Number", "Data"),
        ("attachment_date", "Attachment Date", "Date"),
        ("attachment_end_date", "Attachment End Date", "Date"),
        ("attachment_to_institution_date", "Transfer Date to the Institution", "Date"),
        ("appointed_position", "Appointed Position", "Data"),
        ("service_reinstatement_letter_number", "Service Reinstatement Letter Number", "Data"),
        ("total_duration_of_termination", "Total Duration of Termination", "Small Text"),
        ("attached_from", "Attached From", "Data"),
        ("attached_to", "Attached To", "Data"),
        ("salary_notes_section", "Salary and Notes", "Section Break"),
        ("salary_at_appointment", "Salary at Appointment", "Currency"),
        ("notes", "Notes", "Small Text"),
    ]
    fields = []
    for suffix, label, fieldtype in definitions:
        field = dict(fieldname="custom_mce_" + suffix, label=label, fieldtype=fieldtype)
        if fields:
            field["insert_after"] = fields[-1]["fieldname"]
        if fieldtype == "Currency":
            field["options"] = "salary_currency"
        if suffix == "alternative_phone_number":
            field["options"] = "Phone"
        fields.append(field)
    return fields


def setup_employee_fields():
    preflight_numeric_fields()
    normalize_numeric_storage()
    fields = employee_fields()
    owned = {field["fieldname"] for field in fields}
    retired = RETIRED_FIELDS
    # Preserve ambiguous historical values without assigning them a new meaning.
    archived = []
    for fieldname in retired:
        name = frappe.db.get_value("Custom Field", {"dt": "Employee", "fieldname": fieldname})
        if name:
            field = frappe.get_doc("Custom Field", name)
            if not field.hidden or not field.read_only:
                field.hidden = 1
                field.read_only = 1
                field.save(ignore_permissions=True)
            archived.append(fieldname)
    owned.update(retired)
    order = [field.fieldname for field in frappe.get_meta("Employee").fields if field.fieldname not in owned]
    position = order.index("connections_tab") if "connections_tab" in order else len(order)
    fields[0]["insert_after"] = order[position - 1] if position else ""
    create_custom_fields({"Employee": fields}, update=False)
    for definition in fields:
        name = frappe.db.get_value("Custom Field", {"dt": "Employee", "fieldname": definition["fieldname"]})
        field = frappe.get_doc("Custom Field", name)
        if field.label != definition["label"]:
            field.label = definition["label"]
            field.save(ignore_permissions=True)
    for fieldname, fieldtype in NUMERIC_TYPES.items():
        update_custom_field(fieldname, fieldtype=fieldtype)
    from masar_mce_hrms.employee_behaviour import setup_behaviour
    setup_behaviour()
    update_custom_field("custom_classification", label="Medical Classification", fieldtype="Data", options="")
    if frappe.get_meta("Employee").get_field("employment_type").label != "Military Classification":
        make_property_setter("Employee", "employment_type", "label", "Military Classification", "Data")
    frappe.clear_cache(doctype="Employee")
    from frappe.core.doctype.doctype.doctype import validate_fields_for_doctype
    validate_fields_for_doctype("Employee")
    from masar_mce_hrms.employee_layout import apply_layout
    apply_layout()


RETIRED_FIELDS = {
    "custom_mce_service_type", "custom_mce_health_status", "custom_mce_attachment_location",
    "custom_mce_recruitment_source", "custom_mce_decision_number", "custom_mce_decision_date",
}
NUMERIC_TYPES = {"custom_agg": "Int", "custom_height": "Float", "custom_weight": "Float"}


def preflight_numeric_fields():
    invalid = []
    for row in frappe.get_all("Employee", fields=["name", *NUMERIC_TYPES]):
        for fieldname, fieldtype in NUMERIC_TYPES.items():
            value = row[fieldname]
            if value is None or not str(value).strip():
                continue
            try:
                number = Decimal(str(value).strip())
                valid = number.is_finite() and number >= 0 and (fieldtype != "Int" or number == number.to_integral_value())
            except InvalidOperation:
                valid = False
            if not valid:
                invalid.append(f"{row.name}: {fieldname} = {value!r}")
    if invalid:
        frappe.throw("Correct these Employee values before numeric conversion:<br>" + "<br>".join(frappe.utils.escape_html(value) for value in invalid))


def update_custom_field(fieldname, **changes):
    name = frappe.db.get_value("Custom Field", {"dt": "Employee", "fieldname": fieldname})
    if not name:
        frappe.throw(f"Expected Employee Custom Field {fieldname} is missing")
    field = frappe.get_doc("Custom Field", name)
    if any(field.get(key) != value for key, value in changes.items()):
        if fieldname in NUMERIC_TYPES and field.fieldtype == "Data" and changes.get("fieldtype") == NUMERIC_TYPES[fieldname]:
            # The preflight above establishes that this normally blocked conversion is safe.
            field.flags.ignore_validate = True
        field.update(changes)
        field.save(ignore_permissions=True)


def normalize_numeric_storage():
    # Frappe numeric columns use zero for unset values, rather than empty strings.
    for fieldname in NUMERIC_TYPES:
        frappe.db.sql(f"UPDATE `tabEmployee` SET `{fieldname}` = 0 WHERE `{fieldname}` IS NULL OR TRIM(`{fieldname}`) = ''")
