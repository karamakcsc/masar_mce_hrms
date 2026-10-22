app_name = "masar_mce_hrms"
app_title = "Masar MCE HRMS"
app_publisher = "KCSC"
app_description = "Masar MCE HRMS"
app_email = "info@kcsc.com.jo"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "masar_mce_hrms",
# 		"logo": "/assets/masar_mce_hrms/logo.png",
# 		"title": "Masar MCE HRMS",
# 		"route": "/masar_mce_hrms",
# 		"has_permission": "masar_mce_hrms.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/masar_mce_hrms/css/masar_mce_hrms.css"
# app_include_js = "/assets/masar_mce_hrms/js/masar_mce_hrms.js"

# include js, css files in header of web template
# web_include_css = "/assets/masar_mce_hrms/css/masar_mce_hrms.css"
# web_include_js = "/assets/masar_mce_hrms/js/masar_mce_hrms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "masar_mce_hrms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "masar_mce_hrms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "masar_mce_hrms.utils.jinja_methods",
# 	"filters": "masar_mce_hrms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "masar_mce_hrms.install.before_install"
# after_install = "masar_mce_hrms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "masar_mce_hrms.uninstall.before_uninstall"
# after_uninstall = "masar_mce_hrms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "masar_mce_hrms.utils.before_app_install"
# after_app_install = "masar_mce_hrms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "masar_mce_hrms.utils.before_app_uninstall"
# after_app_uninstall = "masar_mce_hrms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "masar_mce_hrms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Employee": {
		"validate": "masar_mce_hrms.custom.employee.employee.validate",
		"on_update": "masar_mce_hrms.custom.employee.employee.on_update",
		"before_insert": "masar_mce_hrms.custom.employee.employee.before_insert",
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"masar_mce_hrms.tasks.all"
# 	],
	"daily": [
		"masar_mce_hrms.tasks.enqueue_daily_update"
	],
# 	"hourly": [
# 		"masar_mce_hrms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"masar_mce_hrms.tasks.weekly"
# 	],
# 	"monthly": [
# 		"masar_mce_hrms.tasks.monthly"
# 	],
}

# Testing
# -------

# before_tests = "masar_mce_hrms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "masar_mce_hrms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
override_doctype_dashboards = {
	"Employee": "masar_mce_hrms.custom.employee.employee_dashboard.employee_dashboard"
}

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["masar_mce_hrms.utils.before_request"]
# after_request = ["masar_mce_hrms.utils.after_request"]

# Job Events
# ----------
# before_job = ["masar_mce_hrms.utils.before_job"]
# after_job = ["masar_mce_hrms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"masar_mce_hrms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

fixtures = [
    {"dt": "Custom Field", "filters": [
        [
            "name", "in", [
				'Employee-custom_age',
				'Employee-custom_appointed_position',
				'Employee-custom_appointment_certificate_number',
				'Employee-custom_column_break_3wxke',
				'Employee-custom_column_break_5gjk2',
				'Employee-custom_column_break_6asf5',
				'Employee-custom_column_break_7qdn3',
				'Employee-custom_column_break_b86ig',
				'Employee-custom_column_break_exksu',
				'Employee-custom_column_break_hjra8',
				'Employee-custom_column_break_pdoag',
				'Employee-custom_column_break_qylpq',
				'Employee-custom_column_break_si0jf',
				'Employee-custom_dailywage_service_duration',
				'Employee-custom_date_of_appointment',
				'Employee-custom_date_of_appointment_as_daily_worker',
				'Employee-custom_decisions_and_attachments',
				'Employee-custom_department_classification',
				'Employee-custom_educational_attainment',
				'Employee-custom_employee_service_status',
				'Employee-custom_enlistment_date',
				'Employee-custom_eye_color',
				'Employee-custom_height',
				'Employee-custom_identity_and_background',
				'Employee-custom_is_market_department',
				'Employee-custom_is_seconded',
				'Employee-custom_is_staff_officer',
				'Employee-custom_mce_employee_sequence_number',
				'Employee-custom_medical_classification',
				'Employee-custom_military_classification',
				'Employee-custom_military_status',
				'Employee-custom_mothers_name',
				'Employee-custom_national_number',
				'Employee-custom_nationality',
				'Employee-custom_notes',
				'Employee-custom_place_of_birth',
				'Employee-custom_promotion_date_to_current_rank',
				'Employee-custom_rank_upon_appointment',
				'Employee-custom_reason_for_leaving_work',
				'Employee-custom_reinstatement_date',
				'Employee-custom_reinstatement_letter_number',
				'Employee-custom_religion',
				'Employee-custom_remarks',
				'Employee-custom_seconded_from',
				'Employee-custom_seconded_to',
				'Employee-custom_secondment_date',
				'Employee-custom_secondment_end_date',
				'Employee-custom_secondment_letter_number',
				'Employee-custom_section_break_39btp',
				'Employee-custom_section_break_7gns3',
				'Employee-custom_section_break_ei0vo',
				'Employee-custom_section_break_j8tos',
				'Employee-custom_section_break_k0pca',
				'Employee-custom_section_break_kpjdd',
				'Employee-custom_section_break_q2edo',
				'Employee-custom_section_break_wnjja',
				'Employee-custom_section_break_y9unf',
				'Employee-custom_section_break_ylvsa',
				'Employee-custom_service_duration',
				'Employee-custom_service_interruptions',
				'Employee-custom_social_security_number',
				'Employee-custom_subunit',
				'Employee-custom_termination_date',
				'Employee-custom_termination_letter_number',
				'Employee-custom_third_name',
				'Employee-custom_total_length_of_service',
				'Employee-custom_total_suspension_duration',
				'Employee-custom_transfer_date_to_institution',
				'Employee-custom_weight'
			]
		]
	]}, 
    {"dt": "Property Setter", "filters": [
			[
				"name", "in", [
					'Employee-branch-label',
					'Employee-contact_details-hidden',
					'Employee-date_of_joining-read_only',
					'Employee-designation-label',
					'Employee-emergency_contact_details-label',
					'Employee-emergency_phone_number-label',
					'Employee-employment_details-label',
					'Employee-employment_type-in_standard_filter',
					'Employee-employment_type-label',
					'Employee-exit-hidden',
					'Employee-main-field_order',
					'Employee-middle_name-label',
					'Employee-person_to_be_contacted-label'
					]
			]
		]},
]