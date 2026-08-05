from hrms.hr.doctype.overtime_slip.overtime_slip import OvertimeSlip
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
    get_assigned_salary_structure,
)
from frappe.utils import cstr
import frappe
from frappe.utils import time_diff_in_hours, get_datetime


class CustomOvertimeSlip(OvertimeSlip):

    def validate(self):
        super().validate()
        self.update_overtime_totals()

    def _bulk_load_overtime_types(self, overtime_type_names):
        """
        Load overtime type details including custom holiday salary component.
        """
        if not overtime_type_names:
            return {}

        overtime_types_data = frappe.get_all(
            "Overtime Type",
            filters={"name": ["in", list(overtime_type_names)]},
            fields=[
                "name",
                "standard_multiplier",
                "weekend_multiplier",
                "public_holiday_multiplier",
                "applicable_for_weekend",
                "applicable_for_public_holiday",
                "overtime_salary_component",
                "custom_holiday_overtime_salary_component",
                "overtime_calculation_method",
                "hourly_rate",
            ],
        )

        overtime_types = {}
        salary_component_based_types = []

        for ot in overtime_types_data:
            overtime_types[ot.name] = ot

            if ot.overtime_calculation_method == "Salary Component Based":
                salary_component_based_types.append(ot.name)

        if salary_component_based_types:
            salary_components = frappe.get_all(
                "Overtime Salary Component",
                filters={"parent": ["in", salary_component_based_types]},
                fields=["parent", "salary_component"],
            )

            grouped = {}

            for row in salary_components:
                grouped.setdefault(row.parent, []).append(
                    row.salary_component
                )

            for ot in salary_component_based_types:
                overtime_types[ot]["components"] = grouped.get(ot, [])

        return overtime_types

    def update_overtime_totals(self):
        """
        Calculate and store total peak and holiday overtime hours
        on the Overtime Slip.
        """

        self.custom_total_peak_overtime_hours = 0
        self.custom_total_holiday_overtime_hours = 0

        if not self.overtime_details:
            return

        holiday_date_map = self.get_holiday_map()

        peak_hours = 0
        holiday_hours = 0

        for detail in self.overtime_details:
            if holiday_date_map.get(cstr(detail.date)):
                holiday_hours += detail.overtime_duration or 0
            else:
                peak_hours += detail.overtime_duration or 0

        self.custom_total_peak_overtime_hours = peak_hours
        self.custom_total_holiday_overtime_hours = holiday_hours

    # def get_overtime_component_amounts(self):
    #     """
    #     Create separate Additional Salary entries for:
    #     - Working Day Overtime
    #     - Holiday / Weekend Overtime
    #     """

    #     if not self.overtime_details:
    #         return {}

    #     unique_overtime_types = {
    #         row.overtime_type for row in self.overtime_details
    #     }

    #     self.overtime_types = self._bulk_load_overtime_types(
    #         unique_overtime_types
    #     )

    #     holiday_date_map = self.get_holiday_map()

    #     overtime_components = {}

    #     for detail in self.overtime_details:

    #         overtime_type = detail.overtime_type

    #         hourly_rate = self._get_applicable_hourly_rate(
    #             overtime_type,
    #             detail.standard_working_hours,
    #         )

    #         overtime_amount = self.calculate_overtime_amount(
    #             overtime_type,
    #             hourly_rate,
    #             detail.overtime_duration,
    #             detail.date,
    #             holiday_date_map,
    #         )

    #         overtime_config = self.overtime_types[overtime_type]

    #         if holiday_date_map.get(cstr(detail.date)):
    #             salary_component = (
    #                 overtime_config.get(
    #                     "custom_holiday_overtime_salary_component"
    #                 )
    #                 or overtime_config["overtime_salary_component"]
    #             )
    #         else:
    #             salary_component = overtime_config[
    #                 "overtime_salary_component"
    #             ]

    #         overtime_components[salary_component] = (
    #             overtime_components.get(salary_component, 0)
    #             + overtime_amount
    #         )

    #     return overtime_components

    def get_overtime_component_amounts(self):
        """
        Create Additional Salary amounts using custom formulas.

        Peak OT:
            Basic / 30.42 / 8 * Peak Hours * 1.25

        Holiday OT:
            Basic / 30.42 / 8 * Holiday Hours * 1.5
        """

        if not self.overtime_details:
            return {}

        unique_overtime_types = {
            row.overtime_type for row in self.overtime_details
        }

        self.overtime_types = self._bulk_load_overtime_types(
            unique_overtime_types
        )

        if not hasattr(self, "_cached_salary_slip"):
            salary_structure = get_assigned_salary_structure(
                self.employee,
                self.start_date,
            )
            self._cached_salary_slip = self._make_salary_slip(
                salary_structure
            )

        # Get Basic salary
        ssa = frappe.get_value(
            "Salary Structure Assignment",
            {
                "employee": self.employee,
                "docstatus": 1,
                "from_date": ["<=", self.start_date],
            },
            ["name", "base"],
            as_dict=True,
            order_by="from_date desc",
        )

        if not ssa:
            frappe.throw("No Salary Structure Assignment found.")

        basic_salary = ssa.base or 0
        if not basic_salary:
            return {}

        hourly_rate = basic_salary / 30.42 / 8

        peak_amount = round(
            hourly_rate
            * self.custom_total_peak_overtime_hours
            * 1.25,
            2,
        )

        holiday_amount = round(
            hourly_rate
            * self.custom_total_holiday_overtime_hours
            * 1.5,
            2,
        )

        holiday_date_map = self.get_holiday_map()

        peak_component = None
        holiday_component = None

        for detail in self.overtime_details:
            overtime_config = self.overtime_types.get(detail.overtime_type)

            if not overtime_config:
                continue

            if holiday_date_map.get(cstr(detail.date)):
                if not holiday_component:
                    holiday_component = (
                        overtime_config.get(
                            "custom_holiday_overtime_salary_component"
                        )
                        or overtime_config.get(
                            "overtime_salary_component"
                        )
                    )
            else:
                if not peak_component:
                    peak_component = overtime_config.get(
                        "overtime_salary_component"
                    )

            if peak_component and holiday_component:
                break

        overtime_components = {}

        if peak_component and peak_amount > 0:
            overtime_components[peak_component] = peak_amount

        if holiday_component and holiday_amount > 0:
            overtime_components[holiday_component] = holiday_amount

        # frappe.msgprint(f"""
        #     Basic Salary: {basic_salary}
        #     Peak Hours: {self.custom_total_peak_overtime_hours}
        #     Holiday Hours: {self.custom_total_holiday_overtime_hours}
        #     Hourly Rate: {hourly_rate}
        #     Peak Amount: {peak_amount}
        #     Holiday Amount: {holiday_amount}
        #     """)

        return overtime_components

    def _calculate_component_based_hourly_rate(
        self,
        overtime_type,
        standard_working_hours,
    ):
        components = (
            self.overtime_types[overtime_type].get("components") or []
        )

        if not hasattr(self, "_cached_salary_slip"):
            salary_structure = get_assigned_salary_structure(
                self.employee,
                self.start_date,
            )

            self._cached_salary_slip = self._make_salary_slip(
                salary_structure
            )

        if not components or not hasattr(
            self, "_cached_salary_slip"
        ):
            return 0

        component_amount = sum(
            row.amount
            for row in self._cached_salary_slip.earnings
            if row.salary_component in components
            and not row.get("additional_salary")
        )

        payment_days = max(
            self._cached_salary_slip.payment_days,
            1,
        )

        applicable_daily_amount = (
            component_amount / payment_days
        )

        return (
            applicable_daily_amount
            / standard_working_hours
            if standard_working_hours
            else 0
        )


    def get_attendance_records(self):
        records = []

        if self.start_date and self.end_date:
            records = frappe.get_all(
                "Attendance",
                fields=[
                    "name",
                    "attendance_date",
                    "overtime_type",
                    "actual_overtime_duration",
                    "working_hours",              
                    "standard_working_hours",
                    "shift"
                ],
                filters={
                    "employee": self.employee,
                    "docstatus": 1,
                    "attendance_date": (
                        "between",
                        [self.start_date, self.end_date],
                    ),
                    "status": "Present",
                    "overtime_type": ["!=", ""],
                },
            )
        # for r in records:
        #     frappe.msgprint(
        #         f"{r.name} | {r.attendance_date} | {r.overtime_type}"
        #     )
        return records

    def get_shift_hours(self, shift_name, attendance_date):
        shift = frappe.get_cached_doc("Shift Type", shift_name)

        start = get_datetime(f"{attendance_date} {shift.start_time}")
        end = get_datetime(f"{attendance_date} {shift.end_time}")

        if end < start:
            end = frappe.utils.add_days(end, 1)

        return time_diff_in_hours(end, start)
    

    def create_overtime_details_row_for_attendance(self, records):
        # frappe.msgprint("Custom create_overtime_details_row_for_attendance called")
        self.overtime_details = []
        overtime_type_cache = {}

        holiday_date_map = self.get_holiday_map()

        for record in records:
            if record.overtime_type not in overtime_type_cache:
                overtime_type_cache[record.overtime_type] = frappe.db.get_value(
                    "Overtime Type",
                    record.overtime_type,
                    "maximum_overtime_hours_allowed",
                )

            # frappe.msgprint(
            #     f"""
            # Date: {record.attendance_date}
            # Working Hours: {record.working_hours}
            # Actual OT: {record.actual_overtime_duration}
            # Holiday: {holiday_date_map.get(cstr(record.attendance_date))}
            # """
            # )

            maximum_overtime_hours_allowed = overtime_type_cache[
                record.overtime_type
            ]

            # Holiday / Weekly Off -> use working hours
            if holiday_date_map.get(cstr(record.attendance_date)):
                overtime_duration = record.working_hours or 0.0
            else:
                # Working Day -> use actual overtime
                overtime_duration = record.actual_overtime_duration or 0.0

            # Apply maximum overtime limit
            if maximum_overtime_hours_allowed > 0:
                overtime_duration = min(
                    overtime_duration,
                    maximum_overtime_hours_allowed,
                )

            if overtime_duration > 0:
                self.append(
                    "overtime_details",
                    {
                        "reference_document": record.name,
                        "date": record.attendance_date,
                        "overtime_type": record.overtime_type,
                        "overtime_duration": overtime_duration,
                        "standard_working_hours": record.standard_working_hours,
                    },
                )