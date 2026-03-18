import frappe


def leave_application_after_save(doc, method=None):
    """
    Send emails based on workflow_state after save
    """

    if not doc.workflow_state:
        return

    if doc.workflow_state == "Pending GM Approval for OFFICE STAFF":

        users = frappe.get_all(
            "Has Role",
            filters={"role": "General Manager"},
            pluck="parent"
        )

        emails = []
        for user in users:
            email = frappe.db.get_value("User", user, "email")
            enabled = frappe.db.get_value("User", user, "enabled")
            if email and enabled:
                emails.append(email)

        if emails:
            frappe.sendmail(
                recipients=emails,
                subject=f"Leave Approval Required (Office Staff): {doc.name}",
                message=(
                    f"<h3>Leave Approval Required</h3>"
                    f"<p>Office Staff leave application <b>{doc.name}</b> "
                    f"requires General Manager approval.</p>"
                )
            )

    elif doc.workflow_state == "Pending Project Manager":

        users = frappe.get_all(
            "Has Role",
            filters={"role": "Projects Manager"},
            pluck="parent"
        )

        emails = []
        for user in users:
            email = frappe.db.get_value("User", user, "email")
            enabled = frappe.db.get_value("User", user, "enabled")
            if email and enabled:
                emails.append(email)

        if emails:
            frappe.sendmail(
                recipients=emails,
                subject=f"Leave Approval Required: {doc.name}",
                message=(
                    f"<h3>Leave Approval Required</h3>"
                    f"<p>Leave application <b>{doc.name}</b> "
                    f"requires Project Manager approval.</p>"
                )
            )

   
    elif doc.workflow_state == "Pending Approval by Administrative Manager":

        users = frappe.get_all(
            "Has Role",
            filters={"role": "Administrative Manager"},
            pluck="parent"
        )

        emails = []
        for user in users:
            email = frappe.db.get_value("User", user, "email")
            enabled = frappe.db.get_value("User", user, "enabled")
            if email and enabled:
                emails.append(email)

        if emails:
            frappe.sendmail(
                recipients=emails,
                subject=f"Leave Approval Required: {doc.name}",
                message=f"<p>Leave application <b>{doc.name}</b> requires Administrative approval.</p>"
            )


    elif doc.workflow_state == "Pending GM Approval":

        users = frappe.get_all(
            "Has Role",
            filters={"role": "General Manager"},
            pluck="parent"
        )

        emails = []
        for user in users:
            email = frappe.db.get_value("User", user, "email")
            enabled = frappe.db.get_value("User", user, "enabled")
            if email and enabled:
                emails.append(email)

        if emails:
            frappe.sendmail(
                recipients=emails,
                subject=f"Leave Approval Required: {doc.name}",
                message=f"<p>Leave application <b>{doc.name}</b> requires GM approval.</p>"
            )

    
    elif doc.workflow_state == "Pending Accounts Approval":

        users = frappe.get_all(
            "Has Role",
            filters={"role": "Senior Accountant"},
            pluck="parent"
        )

        emails = []
        for user in users:
            email = frappe.db.get_value("User", user, "email")
            enabled = frappe.db.get_value("User", user, "enabled")
            if email and enabled:
                emails.append(email)

        if emails:
            frappe.sendmail(
                recipients=emails,
                subject=f"Leave Approval Required: {doc.name}",
                message=f"<p>Leave application <b>{doc.name}</b> requires Accounts approval.</p>"
            )

    
    elif doc.workflow_state in ("Approved", "Rejected"):

        if doc.employee:
            email = (
                frappe.db.get_value("Employee", doc.employee, "company_email")
                or frappe.db.get_value("Employee", doc.employee, "personal_email")
            )

            if email:
                frappe.sendmail(
                    recipients=[email],
                    subject=f"Leave {doc.workflow_state}: {doc.name}",
                    message=(
                        f"<p>Your leave application <b>{doc.name}</b> "
                        f"has been <b>{doc.workflow_state}</b>.</p>"
                    )
                )