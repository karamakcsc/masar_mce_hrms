import frappe 
from frappe.utils import getdate, today
from dateutil.relativedelta import relativedelta
from frappe import _
from masar_mce_hrms.custom.employee.employee_change_log import create_change_logs


def validate(self, method):
    full_name_update(self)
    validate_appointment_dates(self)
    set_date_of_joining(self)
    calculate_service_durations(self)
    calculate_service_nterruptions(self)
    
def on_update(self, method):
    create_change_logs(self)

def before_insert(self , method):
    set_employee_sequence(self)

def full_name_update(self):
    full_name = f"{self.first_name} {self.middle_name} {self.custom_third_name} {self.last_name}"
    self.employee_name = full_name

def set_employee_sequence(self):
    max_sequence = frappe.db.sql(f"SELECT COALESCE(MAX(custom_mce_employee_sequence_number),0) FROM `tab{self.doctype}`")[0][0]
    self.custom_mce_employee_sequence_number = int(max_sequence) + 1
    
def validate_appointment_dates(self):
    daily_date = self.custom_date_of_appointment_as_daily_worker
    appointment_date = self.custom_date_of_appointment
    if not daily_date and not appointment_date:
        frappe.throw(_("Please set at least one of the following dates: <b>Date of Appointment as Daily Worker</b> or <b>Date of Appointment</b>."))
    if daily_date and appointment_date:
        if getdate(daily_date) >= getdate(appointment_date):
            frappe.throw(_("Date of Appointment as Daily Worker must be earlier than Date of Appointment."))
            
def set_date_of_joining(self):
    dates = [ getdate(date_value) for date_value in (
            self.custom_date_of_appointment_as_daily_worker,
            self.custom_date_of_appointment,
        ) if date_value ]
    if dates:
        self.date_of_joining = min(dates)

def calculate_service_durations(self):
    daily_date = self.custom_date_of_appointment_as_daily_worker
    appointment_date = self.custom_date_of_appointment
    current_date = getdate(self.relieving_date) if self.relieving_date else getdate(today())
    if daily_date:
        start_date = getdate(daily_date)
        end_date = (getdate(appointment_date) if appointment_date else current_date)
        self.custom_dailywage_service_duration = (get_service_duration(start_date, end_date))
    else:
        self.custom_dailywage_service_duration = ""
    if appointment_date:
        self.custom_service_duration = get_service_duration(getdate(appointment_date),current_date,)
    else:
        self.custom_service_duration = ""
    start_dates = [
        getdate(date_value) for date_value in (daily_date, appointment_date) if date_value ]
    if start_dates:
        oldest_date = min(start_dates)
        self.custom_total_length_of_service = (get_service_duration(oldest_date, current_date))

def calculate_service_nterruptions(self):
    if self.custom_termination_date and self.custom_reinstatement_date:
        termination_date = getdate(self.custom_termination_date)
        reinstatement_date = getdate(self.custom_reinstatement_date)
        if termination_date >= reinstatement_date:
            frappe.throw(_("Termination Date must be earlier than Reinstatement Date."))
        self.custom_total_suspension_duration = get_service_duration(termination_date, reinstatement_date)
    else:
        self.custom_total_suspension_duration = ""
        

def get_service_duration(start_date, end_date):
    delta = relativedelta(end_date, start_date)
    return f"\u200F{delta.years} سنة و {delta.months} شهر و {delta.days} يوم"