from decimal import Decimal, InvalidOperation

import frappe
from frappe import _
from frappe.utils import getdate, validate_phone_number
from hrms.overrides.employee_master import EmployeeMaster


class MCEEmployee(EmployeeMaster):
    def set_employee_name(self):
        self.employee_name = " ".join(
            str(self.get(field) or "").strip()
            for field in ("first_name", "middle_name", "custom_third_name", "last_name")
            if str(self.get(field) or "").strip()
        )

    def before_validate(self):
        self.validate_mce_fields()
        from masar_mce_hrms.services.service_duration import calculate_durations
        calculate_durations(self)
        previous = self.get_doc_before_save()
        if previous:
            self.custom_mce_employee_sequence_number = previous.custom_mce_employee_sequence_number

    def before_insert(self):
        from frappe.model.naming import getseries
        maximum = frappe.db.sql("SELECT COALESCE(MAX(custom_mce_employee_sequence_number),0) FROM `tabEmployee`")[0][0]
        frappe.db.sql("INSERT INTO `tabSeries` (name,current) VALUES (%s,%s) ON DUPLICATE KEY UPDATE current=GREATEST(current,VALUES(current))", ("MCE-EMPLOYEE-SEQUENCE", maximum))
        self.custom_mce_employee_sequence_number = int(getseries("MCE-EMPLOYEE-SEQUENCE", 1))

    def onload(self):
        from masar_mce_hrms.services.service_duration import calculate_durations
        calculate_durations(self)

    def validate_mce_fields(self):
        for fieldname in ("custom_age", "custom_height", "custom_weight", "custom_mce_salary_at_appointment"):
            value = self.get(fieldname)
            if value is None or not str(value).strip():
                continue
            try:
                number = Decimal(str(value).strip())
            except InvalidOperation:
                number = Decimal("NaN")
            if not number.is_finite() or number < 0 or (fieldname == "custom_age" and number != number.to_integral_value()):
                frappe.throw(_("{0} must be a non-negative {1}.").format(self.meta.get_label(fieldname), _("whole number") if fieldname == "custom_age" else _("number")))
        for earlier, later in (
            ("custom_mce_attachment_date", "custom_mce_attachment_end_date"),
            ("custom_mce_release_date", "custom_mce_service_reinstatement_date"),
            ("date_of_birth", "custom_mce_enlistment_date"),
            ("custom_mce_enlistment_date", "custom_mce_last_promotion_date"),
        ):
            if self.get(earlier) and self.get(later) and getdate(self.get(later)) < getdate(self.get(earlier)):
                frappe.throw(_("{0} cannot precede {1}.").format(self.meta.get_label(later), self.meta.get_label(earlier)))
        if self.get("custom_mce_alternative_phone_number"):
            validate_phone_number(self.custom_mce_alternative_phone_number, throw=True)
