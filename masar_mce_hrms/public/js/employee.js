function mce_full_name(frm) {
    const name = ["first_name", "middle_name", "custom_third_name", "last_name"]
        .map(field => String(frm.doc[field] || "").trim()).filter(Boolean).join(" ");
    if (frm.doc.employee_name !== name) return frm.set_value("employee_name", name);
}

frappe.ui.form.on("Employee", {
    first_name: mce_full_name,
    middle_name: mce_full_name,
    custom_third_name: mce_full_name,
    last_name: mce_full_name,
    validate(frm) {
        for (const field of ["custom_age", "custom_height", "custom_weight", "custom_mce_salary_at_appointment"]) {
            const value = frm.doc[field];
            if (value === null || value === undefined || value === "") continue;
            const number = Number(value);
            if (!Number.isFinite(number) || number < 0 || (field === "custom_age" && !Number.isInteger(number))) {
                frappe.throw(__("{0} must be a non-negative {1}.", [frm.fields_dict[field].df.label, field === "custom_age" ? __("whole number") : __("number")]));
            }
        }
        return mce_full_name(frm);
    }
});
