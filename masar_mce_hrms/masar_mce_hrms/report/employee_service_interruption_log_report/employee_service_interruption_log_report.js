// Copyright (c) 2026, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Service Interruption Log Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "changed_by",
			label: __("Modified By"),
			fieldtype: "Link",
			options: "User",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (!data) return value;
		if (column.fieldname === "old_value") {
			return `<span style="color: var(--red-600); text-decoration: line-through;">${value}</span>`;
		}
		if (column.fieldname === "new_value") {
			return `<span style="color: var(--green-600); font-weight: 600;">${value}</span>`;
		}
		return value;
	},
};
