
import frappe

@frappe.whitelist()
def add(doctype, name, employee, description=None):
    todo = frappe.get_doc({
        "doctype": "ToDo",
        "reference_type": doctype,
        "reference_name": name,
        "description": description or "Assigned via Project",
        "employee": employee   
    })
    todo.insert(ignore_permissions=True)
    return {"message": f"Task assigned to Employee {employee}"}
