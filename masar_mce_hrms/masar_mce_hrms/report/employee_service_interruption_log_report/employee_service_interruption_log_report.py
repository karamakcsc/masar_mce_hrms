# Copyright (c) 2026, KCSC and contributors
# For license information, please see license.txt

from masar_mce_hrms.custom.employee.employee_change_log import get_change_log_report


def execute(filters=None):
	return get_change_log_report("Employee Service Interruption Log", filters)
