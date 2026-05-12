# Copyright (c) 2026, ERPGulf and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


# class-based version
class ProjectProgress(Document):
    def validate(self):
        duplicate = frappe.db.exists(
            "Project Progress",
            {
                "project": self.project,
                "date":    self.date,
                "name":    ("!=", self.name)
            }
        )
        if duplicate:
            frappe.throw(
                frappe._(
                    "A Project Progress record for project <b>{0}</b> on date <b>{1}</b> "
                    "already exists ({2}). Same project with the same date is not allowed."
                ).format(
                    self.project,
                    frappe.utils.formatdate(self.date),
                    duplicate
                ),
                title=frappe._("Duplicate Entry")
            )