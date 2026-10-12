"""Employee layout only: no Employee saves or behaviour migrations."""

import hashlib
import json

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


GROUPS = {
    "basic_details_tab": [
        "employee_number", "custom_mce_employee_sequence_number", "first_name", "middle_name",
        "custom_third_name", "last_name", "column_break_9", "custom_group", "branch", "department", "employee_name",
        "custom_column_break_bemw2", "gender", "custom_mce_service_status", "custom_mce_notes", "custom_mce_last_promotion_date",
        "custom_mce_department", "custom_mce_enlistment_date",
    ],
    "personal_details": [
        "custom_national_number", "date_of_birth", "custom_mce_place_of_birth", "custom_height",
        "custom_weight", "custom_eye_color", "column_break6", "custom_mothers_name", "custom_nationality",
        "custom_religion", "current_address", "custom_age", "blood_group", "marital_status",
        "cell_number", "custom_mce_education_level", "custom_mce_alternative_phone_number",
    ],
    "employment_details": [
        "employment_type", "designation", "date_of_joining", "custom_mce_appointment_certificate_number",
        "column_break_32", "custom_date_of_appointment_as_daily_worker", "custom_mce_subunit", "custom_military_status",
        "custom_social_security_number", "custom_duration_of_daily_service", "custom_mce_employment_type",
        "col_break_22", "custom_classification", "custom_reason_for_leaving_work", "custom_mce_service_duration",
        "custom_total_length_of_service",
    ],
    "exit": [
        "custom_mce_release_date", "custom_mce_release_letter_number", "custom_mce_service_reinstatement_date",
        "custom_mce_service_reinstatement_letter_number", "custom_mce_total_duration_of_termination",
    ],
}
ATTACHMENTS = [
    "custom_mce_attached_from", "custom_mce_attachment_letter_number", "custom_mce_appointed_position",
    "custom_mce_attached_to", "custom_mce_attachment_end_date", "custom_mce_attachment_date",
    "custom_mce_attachment_to_institution_date", "custom_mce_salary_at_appointment",
]
LAYOUT_FIELDS = {
    "custom_mce_service_details_tab", "custom_mce_personal_service_section",
    "custom_mce_decisions_attachments_section", "custom_mce_salary_notes_section",
}


def set_layout_property(fieldname, property_name, value, property_type="Check"):
    existing = frappe.db.get_value("Property Setter", {
        "doc_type": "Employee", "field_name": fieldname, "property": property_name,
    }, "name")
    if existing:
        setter = frappe.get_doc("Property Setter", existing)
        if str(setter.value) != str(value):
            setter.value = str(value)
            setter.save(ignore_permissions=True)
    else:
        make_property_setter("Employee", fieldname, property_name, str(value), property_type, for_doctype=fieldname is None)


def apply_layout():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    from masar_mce_hrms.customization.employee_layout_config import SECTIONS, TABS

    meta = frappe.get_meta("Employee")
    original_tabs = tab_membership(meta)
    fields = []
    for name, label in SECTIONS.items():
        if any(section == name for blocks in TABS.values() for section, _, _ in blocks):
            fields.append(dict(fieldname=name, label=label, fieldtype="Section Break", insert_after="connections_tab"))
    for blocks in TABS.values():
        for _, column, _ in blocks:
            if column and column.startswith("custom_mce_layout_"):
                fields.append(dict(fieldname=column, fieldtype="Column Break", insert_after="connections_tab"))
    create_custom_fields({"Employee": fields}, update=False)
    meta = frappe.get_meta("Employee")
    by_name = {f.fieldname: f for f in meta.fields}
    original_order = [f.fieldname for f in meta.fields]
    tab_order = [f.fieldname for f in meta.fields if f.fieldtype == "Tab Break"]
    order = [name for name in original_order if name in original_tabs and original_tabs[name] is None and by_name[name].fieldtype != "Tab Break"]
    active_layout = set()
    for tab in tab_order:
        order.append(tab)
        used = {tab}
        for section, column, columns in TABS.get(tab, []):
            if section:
                order.append(section)
                used.add(section)
                active_layout.add(section)
            for index, values in enumerate(columns):
                if index and column:
                    order.append(column)
                    used.add(column)
                    active_layout.add(column)
                for name in values:
                    if name not in by_name:
                        frappe.throw("Missing Employee layout field: " + name)
                    if original_tabs.get(name) != tab:
                        frappe.throw("Employee layout would move a data field to another tab: " + name)
                    order.append(name)
                    used.add(name)
        extras = [name for name in original_order if original_tabs.get(name) == tab and name not in used and not name.startswith("custom_mce_layout_")]
        # Keep extensions and hidden fields in their own tab, ahead of unused breaks.
        order.extend(name for name in extras if by_name[name].fieldtype not in ("Section Break", "Column Break"))
        order.extend(name for name in extras if by_name[name].fieldtype in ("Section Break", "Column Break"))
    assert len(order) == len(set(order)) and set(order) == set(by_name)
    set_layout_property(None, "field_order", json.dumps(order), "Data")
    for field in meta.fields:
        if field.fieldtype in ("Section Break", "Column Break"):
            set_layout_property(field.fieldname, "hidden", 0 if field.fieldname in active_layout else 1)
    set_layout_property("custom_mce_service_details_tab", "hidden", 1)
    frappe.clear_cache(doctype="Employee")


def tab_membership(meta):
    tab = None
    result = {}
    for field in meta.fields:
        if field.fieldtype == "Tab Break":
            tab = field.fieldname
        result[field.fieldname] = tab
    return result


def employee_digest():
    rows = frappe.db.sql("SELECT * FROM `tabEmployee` ORDER BY name", as_dict=True)
    return hashlib.sha256(json.dumps(rows, default=str, sort_keys=True).encode()).hexdigest()


def apply_and_verify():
    from masar_mce_hrms.customization.employee_layout_config import TABS

    before = frappe.get_meta("Employee")
    layout_types = ("Tab Break", "Section Break", "Column Break")
    def definitions(meta):
        return {
            field.fieldname: {key: value for key, value in field.as_dict().items() if key != "idx"}
            for field in meta.fields if field.fieldtype not in layout_types
        }
    data_definitions = definitions(before)
    membership = tab_membership(before)
    digest = employee_digest()
    counts = {name: frappe.db.count(name) for name in ("Employee Leave Log", "Employee Administrative Letter Log")}
    existing_names = {f.fieldname for f in before.fields}
    apply_layout()
    first = [f.fieldname for f in frappe.get_meta("Employee").fields]
    apply_layout()
    after = frappe.get_meta("Employee")
    assert first == [f.fieldname for f in after.fields]
    assert len(first) == len(set(first))
    assert existing_names.issubset(first)
    assert data_definitions == definitions(after), "A data-field property changed"
    after_membership = tab_membership(after)
    assert all(after_membership[name] == membership[name] for name in data_definitions)
    for tab, blocks in TABS.items():
        for section, column, columns in blocks:
            assert all(after_membership[name] == tab for values in columns for name in values)
            if section:
                assert not after.get_field(section).hidden
            if column:
                assert not after.get_field(column).hidden
            assert all(columns) and max(map(len, columns)) - min(map(len, columns)) <= 2
    assert after.get_field("custom_mce_service_details_tab").hidden
    assert digest == employee_digest()
    assert counts == {name: frappe.db.count(name) for name in counts}
    print("PASS: all tabs balanced; layout idempotent; existing fields retained; every data-field property and tab, all Employee values, and log counts unchanged")
