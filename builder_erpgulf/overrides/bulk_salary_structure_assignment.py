import frappe
import erpnext

from frappe import _
from frappe.query_builder.custom import ConstantColumn
from frappe.query_builder.functions import Coalesce
from frappe.query_builder.terms import SubQuery
from frappe.utils import get_link_to_form

from hrms.hr.utils import validate_bulk_tool_fields


from hrms.payroll.doctype.bulk_salary_structure_assignment.bulk_salary_structure_assignment import (
    BulkSalaryStructureAssignment,
)


class CustomBulkSalaryStructureAssignment(BulkSalaryStructureAssignment):
    @frappe.whitelist()
    def get_employees(self, advanced_filters: list) -> list:
        quick_filter_fields = [
            "company",
            "employment_type",
            "branch",
            "department",
            "designation",
            "grade",
        ]

        filters = [
            [d, "=", self.get(d)]
            for d in quick_filter_fields
            if self.get(d)
        ]

        filters += advanced_filters

        Assignment = frappe.qb.DocType("Salary Structure Assignment")

        employees_with_assignments = SubQuery(
            frappe.qb.from_(Assignment)
            .select(Assignment.employee)
            .distinct()
            .where(
                (Assignment.from_date == self.from_date)
                & (Assignment.docstatus == 1)
            )
        )

        Employee = frappe.qb.DocType("Employee")
        Grade = frappe.qb.DocType("Employee Grade")

        query = (
            frappe.qb.get_query(
                Employee,
                fields=[
                    Employee.employee,
                    Employee.employee_name,
                    Employee.grade,
                ],
                filters=filters,
            )
            .where(
                (Employee.status == "Active")
                & (Employee.date_of_joining <= self.from_date)
                & (
                    (Employee.relieving_date > self.from_date)
                    | (Employee.relieving_date.isnull())
                )
                & (Employee.employee.notin(employees_with_assignments))
            )
            .left_join(Grade)
            .on(Employee.grade == Grade.name)
            .select(
                Coalesce(
                    Grade.default_base_pay,
                    0
                ).as_("base"),

                ConstantColumn(0).as_("variable"),

                ConstantColumn(0).as_("custom_food_allowance"),
                ConstantColumn(0).as_("custom_transport_allowance"),
                ConstantColumn(0).as_("custom_hra"),
                ConstantColumn(0).as_("custom_special"),
                ConstantColumn(0).as_("custom_mobile_allowance"),
                ConstantColumn(0).as_("custom_accomodation"),
                ConstantColumn(0).as_("custom_allowance"),
            )
        )

        return query.run(as_dict=True)

    @frappe.whitelist()
    def bulk_assign_structure(self, employees: list) -> None:

        mandatory_fields = [
            "salary_structure",
            "from_date",
            "company",
        ]

        validate_bulk_tool_fields(
            self,
            mandatory_fields,
            employees,
        )

        if len(employees) <= 30:
            return self._bulk_assign_structure(employees)

        frappe.enqueue(
            self._bulk_assign_structure,
            timeout=3000,
            employees=employees,
        )

        frappe.msgprint(
            _(
                "Creation of Salary Structure Assignments has been queued. "
                "It may take a few minutes."
            ),
            alert=True,
            indicator="blue",
        )

    def _bulk_assign_structure(self, employees: list) -> None:

        success = []
        failure = []

        count = 0
        savepoint = "before_salary_assignment"

        for d in employees:

            try:
                frappe.db.savepoint(savepoint)

                assignment = frappe.new_doc(
                    "Salary Structure Assignment"
                )

                # --------------------------------------------
                # Standard Salary Structure Assignment fields
                # --------------------------------------------

                assignment.employee = d["employee"]
                assignment.salary_structure = self.salary_structure
                assignment.company = self.company
                assignment.currency = self.currency
                assignment.payroll_payable_account = (
                    self.payroll_payable_account
                )
                assignment.from_date = self.from_date
                assignment.base = d.get("base", 0)
                assignment.variable = d.get("variable", 0)
                assignment.income_tax_slab = self.income_tax_slab

                # --------------------------------------------
                # Custom Allowance fields
                # --------------------------------------------

                assignment.custom_food_allowance = d.get(
                    "custom_food_allowance", 0
                )

                assignment.custom_transport_allowance = d.get(
                    "custom_transport_allowance", 0
                )

                assignment.custom_hra = d.get(
                    "custom_hra", 0
                )

                assignment.custom_special = d.get(
                    "custom_special", 0
                )

                assignment.custom_mobile_allowance = d.get(
                    "custom_mobile_allowance", 0
                )

                assignment.custom_accomodation = d.get(
                    "custom_accomodation", 0
                )

                assignment.custom_allowance = d.get(
                    "custom_allowance", 0
                )

                # --------------------------------------------
                # Validate payroll payable account
                # --------------------------------------------

                if not assignment.payroll_payable_account:
                    assignment.payroll_payable_account = frappe.db.get_value(
                        "Company",
                        self.company,
                        "default_payroll_payable_account",
                    )

                    if not assignment.payroll_payable_account:
                        frappe.throw(
                            _(
                                'Please set "Default Payroll Payable Account" '
                                "in Company Defaults"
                            )
                        )

                payroll_payable_account_currency = frappe.db.get_value(
                    "Account",
                    assignment.payroll_payable_account,
                    "account_currency",
                )

                company_currency = erpnext.get_company_currency(
                    self.company
                )

                if (
                    payroll_payable_account_currency != self.currency
                    and payroll_payable_account_currency != company_currency
                ):
                    frappe.throw(
                        _(
                            "Invalid Payroll Payable Account. "
                            "The account currency must be {0} or {1}"
                        ).format(
                            self.currency,
                            company_currency,
                        )
                    )

                # --------------------------------------------
                # Save + Submit
                # --------------------------------------------

                assignment.save(ignore_permissions=True)
                assignment.submit()

            except Exception:

                frappe.db.rollback(
                    save_point=savepoint
                )

                frappe.log_error(
                    f"Bulk Assignment - Salary Structure Assignment "
                    f"failed for employee {d['employee']}.",
                    reference_doctype="Salary Structure Assignment",
                )

                failure.append(d["employee"])

            else:

                success.append(
                    {
                        "doc": get_link_to_form(
                            "Salary Structure Assignment",
                            assignment.name,
                        ),
                        "employee": d["employee"],
                    }
                )

            count += 1

            frappe.publish_progress(
                count * 100 / len(employees),
                title=_("Assigning Structure..."),
            )

        frappe.publish_realtime(
            "completed_bulk_salary_structure_assignment",
            message={
                "success": success,
                "failure": failure,
            },
            doctype="Bulk Salary Structure Assignment",
            after_commit=True,
        )