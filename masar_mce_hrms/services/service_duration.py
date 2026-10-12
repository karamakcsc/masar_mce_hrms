import frappe
from dateutil.relativedelta import relativedelta
from frappe.utils import getdate, today


DURATION_FIELDS = ("custom_mce_service_duration", "custom_duration_of_daily_service", "custom_total_length_of_service")


def duration(start, end):
    if not start or not end:
        return ""
    if getdate(end) < getdate(start):
        return ""
    delta = relativedelta(getdate(end), getdate(start))
    return f"{delta.years} سنة، {delta.months} شهر، {delta.days} يوم"


def calculate_durations(doc):
    end = today()
    daily = doc.get("custom_date_of_appointment_as_daily_worker")
    joining = doc.get("date_of_joining")
    doc.custom_mce_service_duration = duration(joining, end)
    doc.custom_duration_of_daily_service = duration(daily, joining)
    doc.custom_total_length_of_service = duration(daily, end) if duration(daily, joining) and duration(joining, end) else ""


def refresh_durations():
    for row in frappe.get_all("Employee", fields=["name", "date_of_joining", "custom_date_of_appointment_as_daily_worker", *DURATION_FIELDS]):
        old = {field: row[field] for field in DURATION_FIELDS}
        calculate_durations(row)
        values = {field: row[field] for field in DURATION_FIELDS if (old[field] or "") != row[field]}
        if values:
            frappe.db.set_value("Employee", row.name, values, update_modified=False)
