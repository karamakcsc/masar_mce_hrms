"""Transactional checks for automatic, immutable Employee snapshots."""

import frappe

from masar_mce_hrms.services.log_snapshots import LOG_DOCTYPES, SHARED_FIELDS


def run():
    frappe.set_user("Administrator")
    try:
        employee = frappe.get_all("Employee", filters={"user_id": ["is", "not set"]}, pluck="name", limit=1)[0]
        doc = frappe.get_doc("Employee", employee)
        counts = {doctype: frappe.db.count(doctype, {"employee": employee}) for doctype in LOG_DOCTYPES}
        doc.custom_mce_notes = "Snapshot verification first"
        doc.save(ignore_permissions=True)
        first = {}
        for doctype in LOG_DOCTYPES:
            meta = frappe.get_meta(doctype)
            assert all(f.read_only for f in meta.fields)
            assert all(not p.create and not p.write and not p.delete and not p.cancel for p in meta.permissions)
            assert frappe.db.count(doctype, {"employee": employee}) == counts[doctype] + 1
            log = frappe.get_last_doc(doctype, filters={"employee": employee})
            first[doctype] = log.name
            for target, source in SHARED_FIELDS.items():
                assert (log.get(target) or "") == (doc.get(source) or "")
            expect_blocked(lambda: frappe.get_doc({"doctype": doctype, "employee": employee}).insert(ignore_permissions=True))
            log.notes = "Tampered"
            expect_blocked(lambda: log.save(ignore_permissions=True))
            expect_blocked(lambda: frappe.delete_doc(doctype, log.name, force=True, ignore_permissions=True))
            expect_blocked(log.cancel)
        doc.save(ignore_permissions=True)
        doc.bio = "Unrelated verification edit"
        doc.save(ignore_permissions=True)
        for doctype in LOG_DOCTYPES:
            assert frappe.db.count(doctype, {"employee": employee}) == counts[doctype] + 1
        doc.custom_mce_notes = "Snapshot verification second"
        doc.custom_group = "ضابط" if doc.custom_group != "ضابط" else "ضابط صف"
        doc.save(ignore_permissions=True)
        for doctype in LOG_DOCTYPES:
            assert frappe.db.count(doctype, {"employee": employee}) == counts[doctype] + 2
            assert frappe.get_doc(doctype, first[doctype]).notes == "Snapshot verification first"
            assert frappe.get_last_doc(doctype, filters={"employee": employee}).notes == "Snapshot verification second"
        print("PASS: shared-field snapshots, one log per save, unrelated/no-op saves ignored, historical values preserved, manual creation/edit/delete/cancel blocked even for Administrator")
    finally:
        frappe.db.rollback()


def expect_blocked(action):
    try:
        action()
    except frappe.ValidationError:
        return
    raise AssertionError("Read-only historical log operation was allowed")
