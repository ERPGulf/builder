import frappe

from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from frappe.utils import add_days, cint, date_diff, flt, getdate
from hrms.payroll.doctype.salary_slip.salary_slip import (
    verify_lwp_days_corrected,
)


class CustomSalarySlip(SalarySlip):

    def get_lwp_holidays_in_leave_applications(self, holidays):
        """
        Count holidays that fall within approved LWP Leave Applications.

        Only Leave Types with is_lwp = 1 are considered.
        Each holiday is counted only once.
        """

        if not holidays:
            return 0

        holiday_dates = {getdate(d) for d in holidays}
        counted_holidays = set()

        leave_applications = frappe.get_all(
            "Leave Application",
            filters={
                "employee": self.employee,
                "status": "Approved",
                "from_date": ["<=", self.end_date],
                "to_date": [">=", self.start_date],
            },
            fields=[
                "name",
                "leave_type",
                "from_date",
                "to_date",
            ],
        )

        for leave in leave_applications:

            is_lwp = frappe.db.get_value(
                "Leave Type",
                leave.leave_type,
                "is_lwp",
            )

            if not is_lwp:
                continue

            leave_from = max(
                getdate(leave.from_date),
                getdate(self.start_date),
            )

            leave_to = min(
                getdate(leave.to_date),
                getdate(self.end_date),
            )

            current_date = leave_from

            while current_date <= leave_to:

                if (
                    current_date in holiday_dates
                    and current_date not in counted_holidays
                ):
                    counted_holidays.add(current_date)

                current_date = add_days(current_date, 1)

        return len(counted_holidays)

    def get_working_days_details(
        self,
        lwp=None,
        for_preview=0,
        lwp_days_corrected=None,
    ):
        payroll_settings = frappe.get_cached_value(
            "Payroll Settings",
            None,
            (
                "payroll_based_on",
                "include_holidays_in_total_working_days",
                "consider_marked_attendance_on_holidays",
                "daily_wages_fraction_for_half_day",
                "consider_unmarked_attendance_as",
            ),
            as_dict=1,
        )

        consider_marked_attendance_on_holidays = (
            payroll_settings.include_holidays_in_total_working_days
            and payroll_settings.consider_marked_attendance_on_holidays
        )

        daily_wages_fraction_for_half_day = (
            flt(payroll_settings.daily_wages_fraction_for_half_day)
            or 0.5
        )

        working_days = date_diff(
            self.end_date,
            self.start_date,
        ) + 1
        self.total_working_days = working_days

        if for_preview:
            self.total_working_days = working_days
            # self.payment_days = working_days
            return

        holidays = self.get_holidays_for_employee(
            self.start_date,
            self.end_date,
        )

        working_days_list = [
            add_days(
                getdate(self.start_date),
                days=day,
            )
            for day in range(0, working_days)
        ]

        if not cint(
            payroll_settings.include_holidays_in_total_working_days
        ):
            working_days_list = [
                i for i in working_days_list
                if i not in holidays
            ]

            working_days -= len(holidays)

            if working_days < 0:
                frappe.throw(
                    "There are more holidays than working days this month."
                )

        if not payroll_settings.payroll_based_on:
            frappe.throw(
                "Please set Payroll based on in Payroll settings"
            )

        manual_absent_days = self.custom_manually_edit_absent_days

        if payroll_settings.payroll_based_on == "Attendance":

            actual_lwp, calculated_absent = (
                self.calculate_lwp_ppl_and_absent_days_based_on_attendance(
                    holidays,
                    daily_wages_fraction_for_half_day,
                    consider_marked_attendance_on_holidays,
                )
            )

            if manual_absent_days:
                absent = flt(self.absent_days)
            else:
                absent = calculated_absent
                self.absent_days = absent

        else:

            actual_lwp = (
                self.calculate_lwp_or_ppl_based_on_leave_application(
                    holidays,
                    working_days_list,
                    daily_wages_fraction_for_half_day,
                )
            )

            absent = 0

        holiday_lwp = self.get_lwp_holidays_in_leave_applications(
            holidays
        )

        actual_lwp += holiday_lwp

        if payroll_settings.payroll_based_on == "Attendance":

            consider_unmarked_attendance_as = (
                payroll_settings.consider_unmarked_attendance_as
                or "Present"
            )

            if (
                consider_unmarked_attendance_as == "Absent"
                and not manual_absent_days
            ):
                unmarked_days = self.get_unmarked_days(
                    payroll_settings.include_holidays_in_total_working_days,
                    holidays,
                )

                self.absent_days += unmarked_days

            half_absent_days = self.get_half_absent_days(
                consider_marked_attendance_on_holidays,
                holidays,
            )

            if not manual_absent_days:
                self.absent_days += (
                    half_absent_days
                    * daily_wages_fraction_for_half_day
                )

        if not lwp:
            lwp = actual_lwp

        elif lwp != actual_lwp:
            frappe.msgprint(
                frappe._(
                    "Leave Without Pay does not match with approved {} records"
                ).format(
                    payroll_settings.payroll_based_on
                )
            )

        self.leave_without_pay = lwp
        self.total_working_days = working_days

        self.payment_days = (
            flt(self.total_working_days)
            - flt(self.absent_days)
            - flt(self.leave_without_pay)
        )

        # Payment days cannot be negative
        self.payment_days = max(self.payment_days, 0)

        if lwp_days_corrected and lwp_days_corrected > 0:
            if verify_lwp_days_corrected(
                self.employee,
                self.start_date,
                self.end_date,
                lwp_days_corrected,
            ):
                self.payment_days += lwp_days_corrected

    # def calculate_component_amounts(self, component_type):
    #     """
    #     Calculate salary component amounts.

    #     When Manual Edit Amount is enabled on the Salary Slip,
    #     preserve manually entered deduction amounts.
    #     """

    #     if component_type == "deductions" and self.custom_manual_edit_amount:

    #         # Store the current deduction amounts before
    #         # standard HRMS recalculates them.
    #         manual_deduction_amounts = {
    #             row.salary_component: flt(row.amount)
    #             for row in self.deductions or []
    #             if row.salary_component
    #         }

    #         # Run the standard HRMS deduction calculation.
    #         super().calculate_component_amounts(component_type)

    #         # Restore the manually entered amounts.
    #         for row in self.deductions or []:
    #             if row.salary_component in manual_deduction_amounts:
    #                 row.amount = manual_deduction_amounts[
    #                     row.salary_component
    #                 ]

    #         return

    #     # Normal HRMS calculation.
    #     super().calculate_component_amounts(component_type)

    def calculate_component_amounts(self, component_type):
        """
        Calculate salary component amounts.

        When Manual Edit Amount is enabled:
        - Existing deduction rows are preserved.
        - Deduction amounts can be manually edited.
        - Deleted deduction rows remain deleted.
        - Newly added deduction rows remain.
        - HRMS does not rebuild deductions from the Salary Structure.

        Earnings continue to use the standard HRMS calculation.
        """

        if component_type == "deductions":

            # When manual deduction editing is enabled,
            # preserve exactly what is currently in the table.
            if self.custom_manual_edit_amount:
                return

            # Normal HRMS deduction calculation
            super().calculate_component_amounts(component_type)
            return

        # Normal HRMS calculation for earnings
        super().calculate_component_amounts(component_type)