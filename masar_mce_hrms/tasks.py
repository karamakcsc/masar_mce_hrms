import frappe
from frappe.utils import getdate, today
from dateutil.relativedelta import relativedelta

def enqueue_daily_update():
    frappe.enqueue(
        "masar_mce_hrms.tasks.update_all_employee_service_durations",
        queue="long",
        timeout=3600,
    )


def update_all_employee_service_durations():
    current_date = getdate(today())
    employees = frappe.get_all("Employee",fields=["name","custom_date_of_appointment_as_daily_worker","custom_date_of_appointment","relieving_date"],)
    updated  , skipped = 0 , 0
    for employee in employees:
        if employee.relieving_date:
            current_date = getdate(employee.relieving_date)
        daily_date = employee.custom_date_of_appointment_as_daily_worker
        appointment_date = employee.custom_date_of_appointment
        if not daily_date and not appointment_date:
            skipped += 1
            continue
        daily_date = getdate(daily_date) if daily_date else None
        appointment_date = (getdate(appointment_date) if appointment_date else None)
        if (daily_date and appointment_date and daily_date >= appointment_date):
            skipped += 1
            continue
        start_dates = [date_value for date_value in (daily_date, appointment_date) if date_value]
        oldest_date = min(start_dates)
        values = {
            "date_of_joining": oldest_date,
            "custom_total_length_of_service": _format_duration(oldest_date, current_date),
        }
        if daily_date:
            daily_end_date = appointment_date or current_date
            values["custom_dailywage_service_duration"] = ( _format_duration(daily_date, daily_end_date))
        else:
            values["custom_dailywage_service_duration"] = ""
        if appointment_date:
            values["custom_service_duration"] = _format_duration(appointment_date, current_date)
        else:
            values["custom_service_duration"] = ""
        frappe.db.set_value("Employee",employee.name,values,update_modified=False,)
        updated += 1
        if updated % 500 == 0:
            frappe.db.commit()
    frappe.db.commit()
    frappe.logger("employee_service_duration").info(
        f"Daily service-duration update completed. "
        f"Updated: {updated}, Skipped: {skipped}"
    )


def _format_duration(start_date, end_date):
    delta = relativedelta(end_date, start_date)
    return f"\u200F{delta.years} سنة و {delta.months} شهر و {delta.days} يوم"