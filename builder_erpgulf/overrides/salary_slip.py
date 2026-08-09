import frappe

from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from frappe.utils import add_days, cint, date_diff, flt, getdate
from hrms.payroll.doctype.salary_slip.salary_slip import verify_lwp_days_corrected


class CustomSalarySlip(SalarySlip):

    def get_working_days_details(self, lwp=None, for_preview=0, lwp_days_corrected=None):
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
            flt(payroll_settings.daily_wages_fraction_for_half_day) or 0.5
        )

        working_days = date_diff(self.end_date, self.start_date) + 1

        if for_preview:
            self.total_working_days = working_days
            self.payment_days = working_days
            return

        holidays = self.get_holidays_for_employee(
            self.start_date,
            self.end_date
        )

        working_days_list = [
            add_days(getdate(self.start_date), days=day)
            for day in range(0, working_days)
        ]

        if not cint(payroll_settings.include_holidays_in_total_working_days):
            working_days_list = [
                i for i in working_days_list if i not in holidays
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
            actual_lwp = self.calculate_lwp_or_ppl_based_on_leave_application(
                holidays,
                working_days_list,
                daily_wages_fraction_for_half_day,
            )

            absent = 0

        if not lwp:
            lwp = actual_lwp

        elif lwp != actual_lwp:
            frappe.msgprint(
                frappe._(
                    "Leave Without Pay does not match with approved {} records"
                ).format(payroll_settings.payroll_based_on)
            )

        self.leave_without_pay = lwp
        self.total_working_days = working_days

        payment_days = self.get_payment_days(
            payroll_settings.include_holidays_in_total_working_days
        )

        if flt(payment_days) > flt(lwp):

            self.payment_days = flt(payment_days) - flt(lwp)

            if payroll_settings.payroll_based_on == "Attendance":
                self.payment_days -= flt(absent)

            consider_unmarked_attendance_as = (
                payroll_settings.consider_unmarked_attendance_as
                or "Present"
            )

            if payroll_settings.payroll_based_on == "Attendance":

                if consider_unmarked_attendance_as == "Absent":

                    unmarked_days = self.get_unmarked_days(
                        payroll_settings.include_holidays_in_total_working_days,
                        holidays,
                    )

                    if manual_absent_days:
                        # Manual Absent Days already contains
                        # the value the user wants to use.
                        pass
                    else:
                        self.absent_days += unmarked_days
                        self.payment_days -= unmarked_days

                half_absent_days = self.get_half_absent_days(
                    consider_marked_attendance_on_holidays,
                    holidays,
                )

                if manual_absent_days:
                    # Do not modify manually entered Absent Days.
                    pass
                else:
                    self.absent_days += (
                        half_absent_days
                        * daily_wages_fraction_for_half_day
                    )

                self.payment_days -= (
                    half_absent_days
                    * daily_wages_fraction_for_half_day
                )

        else:
            self.payment_days = 0

        if lwp_days_corrected and lwp_days_corrected > 0:
            if verify_lwp_days_corrected(
                self.employee,
                self.start_date,
                self.end_date,
                lwp_days_corrected,
            ):
                self.payment_days += lwp_days_corrected