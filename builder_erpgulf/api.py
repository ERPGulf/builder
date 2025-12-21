# # In your custom app: custom_app/api/assign_to.py

# import frappe
# from frappe.desk.form.assign_to import add as original_add

# @frappe.whitelist()
# def add_custom_assignment(doctype, name, employee, description=None):
#     frappe.get_doc({
#         "doctype": "ToDo",
#         "reference_type": doctype,
#         "reference_name": name,
#         "description": description or "Assigned via Project",
#         "allocated_to": employee  # your custom Employee link field
#     }).insert(ignore_permissions=True)

#     return {"message": f"Task assigned to Employee {employee}"}
# my_app/api/assign_to.py
import frappe

@frappe.whitelist()
def add(doctype, name, employee, description=None):
    todo = frappe.get_doc({
        "doctype": "ToDo",
        "reference_type": doctype,
        "reference_name": name,
        "description": description or "Assigned via Project",
        "employee": employee   # use Employee link instead of User
    })
    todo.insert(ignore_permissions=True)
    return {"message": f"Task assigned to Employee {employee}"}
