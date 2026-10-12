"""Installation-contract and existing-site data-preservation checks."""

import json
from pathlib import Path
from unittest.mock import patch

import frappe

from masar_mce_hrms.customization.employee_layout import employee_digest
from masar_mce_hrms.customization.setup import preflight_numeric_fields, setup_employee_fields
from masar_mce_hrms.patches.rename_employee_age import execute


def run():
    from masar_mce_hrms import hooks

    assert "hrms" in hooks.required_apps
    assert not hasattr(hooks, "after_install")
    assert hooks.after_sync == hooks.after_migrate
    root = Path(frappe.get_app_path("masar_mce_hrms"))
    fields = json.loads((root / "fixtures/custom_field.json").read_text())
    names = {field["fieldname"] for field in fields if field["dt"] == "Employee"}
    assert {"custom_age", "custom_height", "custom_weight"}.issubset(names)
    assert "custom_agg" not in names
    with patch("masar_mce_hrms.customization.setup.frappe.db.has_column", return_value=False), patch("masar_mce_hrms.customization.setup.frappe.get_all") as query:
        try:
            preflight_numeric_fields()
        except frappe.ValidationError as error:
            assert "custom_age" in str(error)
        else:
            raise AssertionError("Missing schema was silently ignored")
        assert all(call.args[0] != "Employee" for call in query.call_args_list)
    before = employee_digest()
    counts = {name: frappe.db.count(name) for name in ("Employee Leave Log", "Employee Administrative Letter Log")}
    execute()
    execute()
    setup_employee_fields()
    setup_employee_fields()
    assert before == employee_digest(), "Recurring setup changed Employee values"
    assert counts == {name: frappe.db.count(name) for name in counts}
    assert frappe.get_meta("Employee").get_field("custom_age").fieldtype == "Int"
    assert not frappe.get_meta("Employee").get_field("custom_agg")
    print("PASS: after-sync installation contract, HRMS dependency, portable Age fixtures, explicit schema checks, idempotent migration/setup, all existing Employee values and logs preserved")
