import frappe
from frappe.utils import formatdate, fmt_money


def get_employee_email(employee):
    """Get employee email through Employee -> user_id -> User."""

    user_id = frappe.db.get_value(
        "Employee",
        employee,
        "user_id"
    )

    if not user_id:
        return None

    user = frappe.db.get_value(
        "User",
        user_id,
        ["email", "enabled"],
        as_dict=True
    )

    if not user or not user.enabled:
        return None

    return user.email or user_id


def get_employee_name(employee):
    """Get employee name."""

    return (
        frappe.db.get_value(
            "Employee",
            employee,
            "employee_name"
        )
        or employee
    )


def get_currency(company):
    """Get company's default currency."""

    return frappe.db.get_value(
        "Company",
        company,
        "default_currency"
    )


def send_loan_application_email(doc, method=None):
    """
    Send email when Loan Application is submitted.

    Approved:
        Loan Application Approved - Waiting for Sanction

    Rejected:
        Loan Application Rejected
    """

    # Only process submitted Loan Applications
    if doc.docstatus != 1:
        return

    # Only process Approved or Rejected applications
    if doc.status not in ("Approved", "Rejected"):
        return

    # Get employee email
    email = get_employee_email(doc.applicant)

    if not email:
        frappe.log_error(
            f"Could not find email for employee {doc.applicant}",
            "Loan Application Email"
        )
        return

    # Get employee name
    employee_name = get_employee_name(doc.applicant)

    # Get company currency
    currency = get_currency(doc.company)

    # Format loan amount
    loan_amount = fmt_money(
        doc.loan_amount or 0,
        currency=currency
    )

    # ---------------------------------------------------------
    # APPROVED
    # ---------------------------------------------------------

    if doc.status == "Approved":

        subject = f"Loan Application Approved - {doc.name}"

        message = f"""
        <p>Dear {employee_name},</p>

        <p>
            Your loan application <b>{doc.name}</b> has been
            <b>approved</b>.
        </p>

        <p>
            The loan is currently waiting for sanction.
        </p>

        <table style="
            border-collapse: collapse;
            width: 100%;
            max-width: 600px;
        ">
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">
                    <b>Loan Application</b>
                </td>
                <td style="padding: 8px; border: 1px solid #ddd;">
                    {doc.name}
                </td>
            </tr>

            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">
                    <b>Loan Amount</b>
                </td>
                <td style="padding: 8px; border: 1px solid #ddd;">
                    {loan_amount}
                </td>
            </tr>
        </table>

        <p>
            You will receive another notification once the loan
            has been sanctioned and disbursed.
        </p>

        <p>
            Regards,<br>
            TDI ERP
        </p>
        """

    # ---------------------------------------------------------
    # REJECTED
    # ---------------------------------------------------------

    else:

        subject = f"Loan Application Rejected - {doc.name}"

        message = f"""
        <p>Dear {employee_name},</p>

        <p>
            Your loan application <b>{doc.name}</b> has been
            <b>rejected</b>.
        </p>

        <p>
            If you require further information, please contact
            the HR team.
        </p>

        <p>
            Regards,<br>
            TDI ERP
        </p>
        """

    # Send email
    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=message
    )


def send_loan_disbursement_email(doc, method=None):
    """
    Send email when Loan is sanctioned/disbursed.

    In this implementation, status = "Sanctioned"
    means the loan has been disbursed.
    """

    # Only process submitted Loans
    if doc.docstatus != 1:
        return

    # In your setup, Sanctioned means disbursed
    if doc.status != "Sanctioned":
        return

    # Make sure an applicant exists
    if not doc.applicant:
        return

    # Get employee email
    email = get_employee_email(doc.applicant)

    if not email:
        frappe.log_error(
            f"Could not find email for employee {doc.applicant}",
            "Loan Disbursement Email"
        )
        return

    # Get employee name
    employee_name = get_employee_name(doc.applicant)

    # Get company currency
    currency = get_currency(doc.company)

    # ---------------------------------------------------------
    # GET LOAN AMOUNT FROM LOAN APPLICATION
    # ---------------------------------------------------------

    loan_amount = doc.loan_amount or 0

    if doc.loan_application:
        application_loan_amount = frappe.db.get_value(
            "Loan Application",
            doc.loan_application,
            "loan_amount"
        )

        if application_loan_amount is not None:
            loan_amount = application_loan_amount

    loan_amount = fmt_money(
        loan_amount,
        currency=currency
    )

    # ---------------------------------------------------------
    # REPAYMENT DETAILS FROM LOAN
    # ---------------------------------------------------------

    repayment_start_date = "-"

    if doc.repayment_start_date:
        repayment_start_date = formatdate(
            doc.repayment_start_date
        )

    repayment_frequency = (
        doc.repayment_frequency
        or "-"
    )

    monthly_repayment_amount = fmt_money(
        doc.monthly_repayment_amount or 0,
        currency=currency
    )

    repayment_method = (
        doc.repayment_method
        or "-"
    )

    # repayment_periods is the tenure
    tenure = doc.repayment_periods or 0

    # ---------------------------------------------------------
    # EMAIL
    # ---------------------------------------------------------

    subject = f"Loan Sanctioned and Disbursed - {doc.name}"

    message = f"""
    <p>Dear {employee_name},</p>

    <p>
        Your loan has been <b>sanctioned and disbursed</b>.
    </p>

    <p>
        Please find your loan details below:
    </p>

    <table style="
        border-collapse: collapse;
        width: 100%;
        max-width: 650px;
    ">

        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <b>Loan Application</b>
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {doc.loan_application or "-"}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <b>Loan Amount</b>
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {loan_amount}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <b>Repayment Start Date</b>
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {repayment_start_date}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <b>Repayment Frequency</b>
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {repayment_frequency}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <b>Monthly Repayment Amount</b>
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {monthly_repayment_amount}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <b>Repayment Method</b>
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {repayment_method}
            </td>
        </tr>

        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                <b>Tenure</b>
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {tenure} months
            </td>
        </tr>

    </table>

    <p>
        Please keep this email for your records.
    </p>

    <p>
        Regards,<br>
        TDI ERP
    </p>
    """

    # Send email
    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=message
    )