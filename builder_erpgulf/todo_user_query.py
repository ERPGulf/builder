import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def user_with_employee_id(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT
            u.name AS value,
            CONCAT(e.name, ' - ', e.employee_name) AS label,
            '' AS description
        FROM `tabUser` u
        JOIN `tabEmployee` e ON e.user_id = u.name
        WHERE u.enabled = 1
          AND (e.name LIKE %(txt)s OR e.employee_name LIKE %(txt)s)
        ORDER BY e.employee_name
        LIMIT %(start)s, %(page_len)s
    """, {
        "txt": "%" + txt + "%",
        "start": start,
        "page_len": page_len
    })
