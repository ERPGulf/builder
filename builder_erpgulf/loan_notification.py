import frappe
from frappe.utils import formatdate


def on_loan_application_update(doc, method=None):
    """
    Trigger on Loan Application on_update
    """

    # Send only after submission
    if doc.docstatus != 1:
        return

    employee = frappe.get_doc("Employee", doc.applicant)
    email = employee.company_email or employee.personal_email

    if not email:
        return

    # Prevent duplicate emails
    if not doc.has_value_changed("status") and not doc.has_value_changed("workflow_state"):
        return

    status = (doc.workflow_state or doc.status or "").lower()

    if status == "approved":
        frappe.sendmail(
            recipients=[email],
            subject="Loan Application Approved",
            message=f"""
            Dear {employee.employee_name},<br><br>

            Your loan application has been <b>approved</b>.

            It is currently waiting for sanction by the management.

            You will receive another email once the loan has been sanctioned and disbursed.

            <br><br>
            Regards,<br>
            TDI ERP
            """,
        )

    elif status == "rejected":
        frappe.sendmail(
            recipients=[email],
            subject="Loan Application Rejected",
            message=f"""
            Dear {employee.employee_name},<br><br>

            We regret to inform you that your loan application has been <b>rejected</b>.

            Please contact HR for further details.

            <br><br>
            Regards,<br>
            TDI ERP
            """,
        )


def on_loan_submit(doc, method=None):
    """
    Trigger on Loan on_submit
    """

    employee = frappe.get_doc("Employee", doc.applicant)
    email = employee.company_email or employee.personal_email

    if not email:
        return

    requested_amount = None

    if doc.loan_application:
        requested_amount = frappe.db.get_value(
            "Loan Application",
            doc.loan_application,
            "loan_amount",
        )

    # Calculate tenure
    tenure = len(doc.repayment_schedule or [])

    frappe.sendmail(
        recipients=[email],
        subject="Loan Sanctioned and Disbursed",
        message=f"""
        Dear {employee.employee_name},<br><br>

        Your loan has been <b>sanctioned and disbursed</b> successfully.

        <table border="1" cellpadding="6" cellspacing="0">
            <tr>
                <td><b>Requested Amount</b></td>
                <td>{requested_amount}</td>
            </tr>
            <tr>
                <td><b>Approved Loan Amount</b></td>
                <td>{doc.loan_amount}</td>
            </tr>
            <tr>
                <td><b>Repayment Start Date</b></td>
                <td>{formatdate(doc.repayment_start_date)}</td>
            </tr>
            <tr>
                <td><b>Repayment Frequency</b></td>
                <td>{doc.repayment_frequency}</td>
            </tr>
            <tr>
                <td><b>Monthly Repayment Amount</b></td>
                <td>{doc.monthly_repayment_amount}</td>
            </tr>
            <tr>
                <td><b>Repayment Method</b></td>
                <td>{doc.repayment_method}</td>
            </tr>
            <tr>
                <td><b>Tenure</b></td>
                <td>{tenure} Months</td>
            </tr>
        </table>

        <br><br>

        Regards,<br>
        TDI ERP
        """,
    )