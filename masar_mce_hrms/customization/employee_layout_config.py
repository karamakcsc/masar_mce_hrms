"""Sections with ordered columns; all data fields retain their current tab."""

SECTIONS = {
    "custom_mce_layout_service": "Service Information",
    "custom_mce_layout_appointment": "Appointment and Employment",
    "custom_mce_layout_duration": "Service Dates and Durations",
    "custom_mce_layout_contract": "Confirmation and Contract",
    "custom_mce_layout_identity": "Identity and Background",
    "custom_mce_layout_health": "Physical and Health Details",
    "custom_mce_layout_contact": "Personal Contact Details",
    "custom_mce_layout_termination": "Termination and Reinstatement",
    "custom_mce_layout_exit": "Exit Arrangements",
}

# Each entry is (existing/new Section Break, existing/new Column Break, columns).
TABS = {
    "basic_details_tab": [
        ("basic_information", "column_break_9", [
            ["salutation", "first_name", "middle_name", "custom_third_name", "last_name"],
            ["employee_name", "employee_number", "custom_mce_employee_sequence_number", "gender", "status"],
        ]),
        ("company_details_section", "column_break_25", [
            ["company", "custom_group", "branch", "department", "custom_mce_department", "reports_to"],
            ["custom_mce_service_status", "grade", "custom_mce_enlistment_date", "custom_mce_last_promotion_date", "custom_mce_notes"],
        ]),
        ("erpnext_user", None, [["user_id", "create_user", "create_user_permission"]]),
    ],
    "employment_details": [
        ("custom_mce_layout_appointment", "column_break_32", [
            ["designation", "employment_type", "custom_mce_employment_type", "custom_mce_subunit"],
            ["custom_military_status", "custom_social_security_number", "custom_classification", "custom_reason_for_leaving_work"],
        ]),
        ("custom_mce_layout_duration", "col_break_22", [
            ["date_of_joining", "custom_mce_appointment_certificate_number", "custom_date_of_appointment_as_daily_worker"],
            ["custom_mce_service_duration", "custom_duration_of_daily_service", "custom_total_length_of_service"],
        ]),
        ("custom_mce_layout_contract", "custom_column_break_qv8tp", [
            ["job_applicant", "scheduled_confirmation_date", "final_confirmation_date"],
            ["contract_end_date", "notice_number_of_days", "date_of_retirement"],
        ]),
        ("custom_mce_decisions_attachments_section", "custom_mce_layout_attachment_column", [
            ["custom_mce_attached_from", "custom_mce_attached_to", "custom_mce_appointed_position", "custom_mce_attachment_letter_number"],
            ["custom_mce_attachment_date", "custom_mce_attachment_end_date", "custom_mce_attachment_to_institution_date", "custom_mce_salary_at_appointment"],
        ]),
    ],
    "contact_details": [
        (None, "column_break_40", [
            ["personal_email", "company_email"],
            ["prefered_contact_email", "prefered_email", "unsubscribed"],
        ]),
        ("address_section", "column_break_46", [
            ["permanent_address", "permanent_accommodation_type"], ["current_accommodation_type"],
        ]),
        ("emergency_contact_details", "column_break_55", [
            ["person_to_be_contacted", "relation"], ["emergency_phone_number"],
        ]),
    ],
    "attendance_and_leave_details": [
        (None, "column_break_44", [["attendance_device_id"], ["holiday_list", "default_shift"]]),
        ("approvers_section", "column_break_45", [["leave_approver", "expense_approver"], ["shift_request_approver"]]),
    ],
    "salary_information": [
        (None, "salary_cb", [["salary_currency", "ctc"], ["salary_mode", "payroll_cost_center"]]),
        ("bank_details_section", "column_break_heye", [["bank_name", "bank_ac_no"], ["iban"]]),
    ],
    "personal_details": [
        ("custom_mce_layout_identity", "column_break6", [
            ["custom_national_number", "date_of_birth", "custom_age", "custom_mce_place_of_birth"],
            ["custom_mothers_name", "custom_nationality", "custom_religion", "custom_mce_education_level"],
        ]),
        ("custom_mce_personal_service_section", "custom_mce_layout_family_column", [["marital_status", "family_background"], ["current_address"]]),
        ("custom_mce_layout_health", "custom_mce_layout_health_column", [
            ["custom_height", "custom_weight", "custom_eye_color"], ["blood_group", "health_details"],
        ]),
        ("custom_mce_layout_contact", "custom_mce_layout_contact_column", [["cell_number"], ["custom_mce_alternative_phone_number"]]),
        ("health_insurance_section", "custom_mce_layout_insurance_column", [["health_insurance_provider"], ["health_insurance_no"]]),
        ("passport_details_section", "column_break_73", [["passport_number", "place_of_issue"], ["date_of_issue", "valid_upto"]]),
    ],
    "profile_tab": [
        (None, None, [["bio"]]),
        ("educational_qualification", None, [["education"]]),
        ("previous_work_experience", None, [["external_work_history"]]),
        ("history_in_company", None, [["internal_work_history"]]),
        ("custom_administrative__books", None, [["custom_penalty"]]),
    ],
    "exit": [
        ("custom_mce_layout_termination", "exit_interview_details", [
            ["custom_mce_release_date", "custom_mce_release_letter_number", "custom_mce_total_duration_of_termination"],
            ["custom_mce_service_reinstatement_date", "custom_mce_service_reinstatement_letter_number"],
        ]),
        ("custom_mce_layout_exit", "column_break_99", [
            ["resignation_letter_date", "relieving_date", "new_workplace"],
            ["held_on", "leave_encashed", "encashment_date"],
        ]),
        ("feedback_section", "column_break_104", [["reason_for_leaving"], ["feedback"]]),
    ],
}
