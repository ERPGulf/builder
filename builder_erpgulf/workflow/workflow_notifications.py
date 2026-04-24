import frappe


def email_notification(doc, method):
    before = doc.get_doc_before_save()

    if not before or before.workflow_state == doc.workflow_state:
        return

    if not doc.workflow_state or doc.workflow_state == "Open":
        return

    def get_emails_by_role(role):
        users = frappe.get_all(
            "Has Role",
            filters={"role": role},
            pluck="parent"
        )
        emails = []
        for user in users:
            email, enabled = frappe.db.get_value("User", user, ["email", "enabled"])
            if email and enabled:
                emails.append(email)
        return emails

    # ================= OFFICE STAFF FLOW =================

    if doc.workflow_state == "Pending Admin Manager Approval for OFFICE STAFF":
        emails = get_emails_by_role("Administrative Manager")
        subject = f"{doc.doctype} Approval Required (Office Staff): {doc.name}"
        message = f"""
            <h3>{doc.doctype} Approval Required</h3>
            <p>Office Staff request <b>{doc.name}</b> requires Administrative Manager approval.</p>
        """

    elif doc.workflow_state == "Pending GM Approval for OFFICE STAFF":
        emails = get_emails_by_role("General Manager")
        subject = f"{doc.doctype} Approval Required (Office Staff): {doc.name}"
        message = f"""
            <h3>{doc.doctype} Approval Required</h3>
            <p>Office Staff request <b>{doc.name}</b> requires General Manager approval.</p>
        """

    elif doc.workflow_state == "Pending Accountant Approval for OFFICE STAFF":
        emails = get_emails_by_role("Senior Accountant")
        subject = f"{doc.doctype} Approval Required (Office Staff): {doc.name}"
        message = f"""
            <h3>{doc.doctype} Approval Required</h3>
            <p>Office Staff request <b>{doc.name}</b> requires Accounts approval.</p>
        """

    # ================= NON-OFFICE STAFF FLOW =================

    elif doc.workflow_state == "Pending Project Manager":
        emails = get_emails_by_role("Projects Manager")
        subject = f"{doc.doctype} Approval Required: {doc.name}"
        message = f"<p>Request <b>{doc.name}</b> requires Project Manager approval.</p>"

    elif doc.workflow_state == "Pending Approval by Administrative Manager":
        emails = get_emails_by_role("Administrative Manager")
        subject = f"{doc.doctype} Approval Required: {doc.name}"
        message = f"<p>Request <b>{doc.name}</b> requires Administrative Manager approval.</p>"

    elif doc.workflow_state == "Pending GM Approval":
        emails = get_emails_by_role("General Manager")
        subject = f"{doc.doctype} Approval Required: {doc.name}"
        message = f"<p>Request <b>{doc.name}</b> requires GM approval.</p>"

    elif doc.workflow_state == "Pending Accounts Approval":
        emails = get_emails_by_role("Senior Accountant")
        subject = f"{doc.doctype} Approval Required: {doc.name}"
        message = f"<p>Request <b>{doc.name}</b> requires Accounts approval.</p>"


    elif doc.workflow_state in ("Approved", "Rejected"):
        creator_email = frappe.db.get_value("User", doc.owner, "email")

        if not creator_email and getattr(doc, "employee", None):
            creator_email = (
                frappe.db.get_value("Employee", doc.employee, "company_email")
                or frappe.db.get_value("Employee", doc.employee, "personal_email")
            )

        if creator_email:
            frappe.sendmail(
                recipients=[creator_email],
                subject=f"{doc.doctype} {doc.workflow_state}: {doc.name}",
                message=f"""
                    <h3>{doc.doctype} Update</h3>
                    <p>Your request <b>{doc.name}</b> has been <b>{doc.workflow_state}</b>.</p>
                """
            )
        return

    else:
        return

    if emails:
        frappe.sendmail(
            recipients=emails,
            subject=subject,
            message=message
        )


def set_initial_workflow_state(doc, method):
    """
    Runs after insert for multiple DocTypes
    Sets initial workflow state based on employee grade
    """

    if doc.workflow_state != "Open":
        return

    if getattr(doc, "custom_employee_grade", None) == "OFFICE STAFF":
        new_state = "Pending Admin Manager Approval for OFFICE STAFF"
    else:
        new_state = "Pending Project Manager"

    doc.db_set("workflow_state", new_state, update_modified=False)