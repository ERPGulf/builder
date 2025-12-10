import frappe

def update_user_from_employee(doc, method):
    if not doc.user_id:
        return

    if not frappe.db.exists("User", doc.user_id):
        return

    user = frappe.get_doc("User", doc.user_id)

    user.employee_id = doc.name
    user.designation = doc.designation

    user.save(ignore_permissions=True)
