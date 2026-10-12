"""Transactional verification: bench --site mce.local execute masar_mce_hrms.verify.run."""

import frappe

from masar_mce_hrms.setup import RETIRED_FIELDS, employee_fields, setup_employee_fields


def run():
    frappe.set_user("Administrator")
    try:
        before = [(f.fieldname, f.label) for f in frappe.get_meta("Employee").fields]
        setup_employee_fields()
        setup_employee_fields()
        meta = frappe.get_meta("Employee")
        after = [(f.fieldname, f.label) for f in meta.fields]
        assert before == after, "Repeated setup changed Employee metadata"
        definitions = employee_fields()
        names = [f.fieldname for f in meta.fields]
        from masar_mce_hrms.employee_layout import GROUPS, ATTACHMENTS, tab_membership
        membership = tab_membership(meta)
        assert len(names) == len(set(names))
        assert meta.get_field("custom_mce_service_details_tab").hidden
        for tab, group in GROUPS.items():
            assert all(membership[name] == tab for name in group)
        assert all(membership[name] == "employment_details" for name in ATTACHMENTS)
        assert sum(f["fieldtype"] not in ("Tab Break", "Section Break") for f in definitions) == 26
        for fieldname in RETIRED_FIELDS:
            field = meta.get_field(fieldname)
            if field:
                assert field.hidden and field.read_only
        assert meta.get_field("custom_agg").fieldtype == "Int"
        assert meta.get_field("custom_height").fieldtype == "Float"
        assert meta.get_field("custom_weight").fieldtype == "Float"
        assert meta.get_field("custom_classification").fieldtype == "Data"
        assert meta.get_field("employment_type").label == "Military Classification"
        assert meta.get_field("custom_mce_release_date").label == "Termination Date"
        assert meta.get_field("custom_mce_attached_from") and meta.get_field("custom_mce_attached_to")
        employee = frappe.db.get_value("Employee", {}, "name")
        assert employee, "An existing Employee is required for verification"
        from masar_mce_hrms.verify_logs import run as verify_logs
        verify_logs()
        dashboard = meta.get_dashboard_data()
        items = [item for group in dashboard.transactions for item in group["items"]]
        assert "Employee Administrative Letter Log" in items and "Employee Leave Log" in items
        verify_employee_validation()
        print("PASS: 25 verified fields, numeric types, archived false fields, repeat setup, four-part names, numeric/date/phone validation, unchanged log protections")
    finally:
        frappe.db.rollback()


def verify_employee_validation():
    from unittest.mock import patch
    from hrms.overrides.employee_master import EmployeeMaster
    from masar_mce_hrms.employee import MCEEmployee
    from masar_mce_hrms.setup import preflight_numeric_fields

    with patch("masar_mce_hrms.setup.frappe.get_all", return_value=[frappe._dict(name="invalid-test", custom_agg="jgjh", custom_height="155gh", custom_weight="12jhg")]):
        expect_validation_error(preflight_numeric_fields)

    doc = frappe.get_doc({"doctype": "Employee", "first_name": " Ahmad ", "middle_name": " Ali ", "custom_third_name": " Hasan ", "last_name": " Saleh "})
    assert isinstance(doc, MCEEmployee) and isinstance(doc, EmployeeMaster)
    doc.set_employee_name()
    assert doc.employee_name == "Ahmad Ali Hasan Saleh"
    doc.custom_third_name = ""
    doc.set_employee_name()
    assert doc.employee_name == "Ahmad Ali Saleh"
    doc.first_name = "\u0623\u062d\u0645\u062f"
    doc.middle_name = "\u0639\u0644\u064a"
    doc.custom_third_name = "\u062d\u0633\u0646"
    doc.last_name = "\u0635\u0627\u0644\u062d"
    doc.set_employee_name()
    assert doc.employee_name == "\u0623\u062d\u0645\u062f \u0639\u0644\u064a \u062d\u0633\u0646 \u0635\u0627\u0644\u062d"
    doc.run_method("before_validate")
    for fieldname, valid in (("custom_agg", 30), ("custom_height", 175.5), ("custom_weight", 72.25)):
        doc.set(fieldname, valid)
    doc.run_method("before_validate")
    for fieldname in ("custom_agg", "custom_height", "custom_weight", "custom_mce_salary_at_appointment"):
        original = doc.get(fieldname)
        for invalid in ("not numeric", -1, "NaN", "Infinity", *([1.5] if fieldname == "custom_agg" else [])):
            doc.set(fieldname, invalid)
            expect_validation_error(lambda: doc.run_method("before_validate"))
        doc.set(fieldname, original)
    for earlier, later in (("custom_mce_attachment_date", "custom_mce_attachment_end_date"), ("custom_mce_release_date", "custom_mce_service_reinstatement_date"), ("date_of_birth", "custom_mce_enlistment_date"), ("custom_mce_enlistment_date", "custom_mce_last_promotion_date")):
        doc.set(earlier, "2020-01-02")
        doc.set(later, "2020-01-01")
        expect_validation_error(lambda: doc.run_method("before_validate"))
        doc.set(later, "2020-01-02")
        doc.run_method("before_validate")
        doc.set(earlier, None)
        doc.set(later, None)
    doc.custom_mce_alternative_phone_number = "invalid phone"
    expect_validation_error(lambda: doc.run_method("before_validate"))
    doc.custom_mce_alternative_phone_number = "+962790000000"
    doc.run_method("before_validate")
    # Exercise the ordinary save path, with transaction rollback in run().
    employee = frappe.get_all("Employee", filters={"user_id": ["is", "not set"]}, pluck="name", limit=1)[0]
    saved = frappe.get_doc("Employee", employee)
    saved.first_name = "Ahmad"
    saved.middle_name = "Ali"
    saved.custom_third_name = "Hasan"
    saved.last_name = "Saleh"
    saved.custom_height = 175.5
    saved.custom_weight = 72.25
    saved.custom_agg = 30
    saved.save(ignore_permissions=True)
    assert saved.employee_name == "Ahmad Ali Hasan Saleh"
    saved.custom_agg = 30.5
    expect_validation_error(lambda: saved.save(ignore_permissions=True))


def expect_validation_error(action):
    try:
        action()
    except frappe.ValidationError:
        return
    raise AssertionError("Invalid Employee input was accepted")
