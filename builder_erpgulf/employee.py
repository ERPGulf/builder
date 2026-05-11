# import frappe


# def on_submit(doc, method=None):
#     _create_additional_salary(doc)


# def on_cancel(doc, method=None):
#     _cancel_additional_salary(doc)


# def _create_additional_salary(doc):

#     # 1. Fetch deduction component from Payroll Settings
#     salary_component = frappe.db.get_single_value(
#         "Payroll Settings", "salary_deduction_component"
#     )
#     if not salary_component:
#         frappe.throw("Salary Deduction Component is not set in Payroll Settings.")

#     # 2. Validate required fields
#     if not doc.grievance_against:
#         frappe.throw("Grievance Against (Employee) is missing.")

#     if not doc.custom_payroll_date:
#         frappe.throw("Custom Payroll Date is missing on the grievance.")

#     if not doc.custom_salary_deduction:
#         frappe.throw("Custom Salary Deduction amount is missing on the grievance.")

#     # 3. Get company from employee record
#     company = frappe.db.get_value("Employee", doc.grievance_against, "company")
#     if not company:
#         frappe.throw(f"Could not find Company for Employee {doc.grievance_against}.")

#     # 4. Create Additional Salary
#     additional_salary = frappe.new_doc("Additional Salary")
#     additional_salary.update({
#         "employee"                        : doc.grievance_against,
#         "salary_component"                : salary_component,
#         "amount"                          : doc.custom_salary_deduction,
#         "payroll_date"                    : doc.custom_payroll_date,
#         "company"                         : company,
#         "overwrite_salary_structure_amount": 0,
#         "ref_doctype"                     : doc.doctype,
#         "ref_docname"                     : doc.name,
#     })
#     additional_salary.insert(ignore_permissions=True)

#     # 5. Store link back on the grievance for cancel lookup
    
#     frappe.msgprint(
#         f"Additional Salary <b>{additional_salary.name}</b> created for "
#         f"Employee {doc.grievance_against}.",
#         alert=True,
#     )


import frappe


def on_submit(doc, method=None):
    _create_additional_salary(doc)




def _create_additional_salary(doc):

    # 1. Fetch salary component where custom_salary_deduction_component=1 AND type=Deduction
    components = frappe.db.get_all(
        "Salary Component",
        filters={
            "custom_salary_deduction_component": 1,
            "type": "Deduction",
        },
        fields=["name"],
    )

    # Validation: must have exactly one such component
    if not components:
        frappe.throw(
            "No Salary Component found with <b>Salary Deduction Component</b> "
            "checkbox ticked and Type = <b>Deduction</b>. "
            "Please configure exactly one such component."
        )

    if len(components) > 1:
        names = ", ".join(c.name for c in components)
        frappe.throw(
            f"Multiple Salary Components ({names}) have the "
            "<b>Salary Deduction Component</b> checkbox ticked with Type = <b>Deduction</b>. "
            "Only one is allowed. Please untick the others."
        )

    salary_component = components[0].name

    # 2. Validate required fields on the grievance
    if not doc.grievance_against:
        frappe.throw("Grievance Against (Employee) is missing.")

    if not doc.custom_payroll_date:
        frappe.throw("Custom Payroll Date is missing on the grievance.")

    if not doc.custom_salary_deduction:
        frappe.throw("Custom Salary Deduction amount is missing on the grievance.")

    # 3. Get company from employee record
    company = frappe.db.get_value("Employee", doc.grievance_against, "company")
    if not company:
        frappe.throw(f"Could not find Company for Employee {doc.grievance_against}.")

    # 4. Create Additional Salary
    additional_salary = frappe.new_doc("Additional Salary")
    additional_salary.update({
        "employee"                         : doc.grievance_against,
        "salary_component"                 : salary_component,
        "amount"                           : doc.custom_salary_deduction,
        "payroll_date"                     : doc.custom_payroll_date,
        "company"                          : company,
        "overwrite_salary_structure_amount": 0,
        "ref_doctype"                      : doc.doctype,
        "ref_docname"                      : doc.name,
    })
    additional_salary.insert(ignore_permissions=True)
    additional_salary.submit()

    # 5. Notify
    frappe.msgprint(
        f"Additional Salary <b>{additional_salary.name}</b> created for "
        f"Employee {doc.grievance_against} using component <b>{salary_component}</b>.",
        alert=True,
    )

import frappe


def before_save(doc, method=None):
    # Only validate when the checkbox is ticked AND type is Deduction
    if not doc.custom_salary_deduction_component or doc.type != "Deduction":
        return

    # Check if any OTHER Salary Component already has the same combo
    existing = frappe.db.get_all(
        "Salary Component",
        filters={
            "custom_salary_deduction_component": 1,
            "type": "Deduction",
            "name": ["!=", doc.name],   # exclude current doc
        },
        fields=["name"],
        limit=1,
    )

    if existing:
        frappe.throw(
            f"Salary Component <b>{existing[0].name}</b> already has "
            "<b>Salary Deduction Component</b> ticked with Type = <b>Deduction</b>. "
            "Only one such component is allowed. Please untick it before enabling another."
        )
