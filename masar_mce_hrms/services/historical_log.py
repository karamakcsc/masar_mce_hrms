import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class HistoricalLog(Document):
    def validate(self):
        from masar_mce_hrms.services.log_snapshots import AUTOMATIC_LOG_TOKEN

        if not self.is_new():
            frappe.throw(_("Historical log records are read-only."))
        if self.flags.mce_log_token is not AUTOMATIC_LOG_TOKEN:
            frappe.throw(_("Historical log records are created automatically from Employee changes."))
        if self.docstatus != 0:
            frappe.throw(_("Historical logs must remain in Draft status."))
        for fieldname in ("penalty_days", "number_of_days", "leave_duration"):
            value = self.get(fieldname)
            if value is not None and value < 0:
                frappe.throw(_("{0} cannot be negative.").format(self.meta.get_label(fieldname)))
        for earlier, later in (("request_date", "start_date"), ("start_date", "end_date"), ("request_date", "end_date")):
            if self.get(earlier) and self.get(later) and getdate(self.get(earlier)) > getdate(self.get(later)):
                frappe.throw(_("{0} cannot precede {1}.").format(self.meta.get_label(later), self.meta.get_label(earlier)))

    def before_cancel(self):
        frappe.throw(_("Historical logs cannot be cancelled."))

    def on_trash(self):
        frappe.throw(_("Historical logs cannot be deleted."))
