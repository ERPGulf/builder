import frappe

def calculate_gross_salary(doc, method):
    base = doc.base or 0
    food = doc.custom_food_allowance or 0
    transport = doc.custom_transport_allowance or 0
    variable = doc.variable or 0
    accomodation = doc.custom_accomodation or 0
    special = doc.custom_special or 0

    gross_salary = base + food + transport + variable + accomodation + special
    doc.gross_salary = gross_salary 

    frappe.msgprint(f"Gross Salary Calculated: {gross_salary}", alert=True)



def validate_advance_limit(doc, method):
    ssa = frappe.get_value(
        "Salary Structure Assignment", 
        {"employee": doc.employee, "docstatus": 1},
        ["gross_salary"]
    )

    if not ssa:
        frappe.throw("No approved Salary Structure Assignment found for this employee")

    gross_salary = ssa or 0
    max_advance = gross_salary * 0.50

    if doc.advance_amount > max_advance:
        frappe.throw(
            f"Maximum advance allowed is 50% of Gross Salary ({max_advance})."
        )



@frappe.whitelist()
def get_allowed_advance(employee):
    gross_salary = frappe.get_value(
        "Salary Structure Assignment",
        {"employee": employee, "docstatus": 1},
        "gross_salary"
    )

    if not gross_salary:
        return 0
    
    return float(gross_salary) * 0.50
