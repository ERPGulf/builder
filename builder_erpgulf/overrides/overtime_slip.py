from hrms.hr.doctype.overtime_slip.overtime_slip import OvertimeSlip
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
    get_assigned_salary_structure,
)
from frappe.utils import cstr
import frappe


class CustomOvertimeSlip(OvertimeSlip):

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
                grouped.setdefault(row.parent, []).append(row.salary_component)

            for ot in salary_component_based_types:
                overtime_types[ot]["components"] = grouped.get(ot, [])

        return overtime_types

    def get_overtime_component_amounts(self):
        """
        Create separate Additional Salary entries for:
        - Working Day Overtime
        - Holiday / Weekend Overtime

        Also stores:
        - custom_peak_overtime_hours
        - custom_holiday_overtime_hours
        """

        if not self.overtime_details:
            self.custom_peak_overtime_hours = 0
            self.custom_holiday_overtime_hours = 0
            return {}

        unique_overtime_types = {
            row.overtime_type for row in self.overtime_details
        }

        self.overtime_types = self._bulk_load_overtime_types(
            unique_overtime_types
        )

        holiday_date_map = self.get_holiday_map()

        overtime_components = {}

        peak_ot_hours = 0.0
        holiday_ot_hours = 0.0

        for detail in self.overtime_details:

            overtime_type = detail.overtime_type

            hourly_rate = self._get_applicable_hourly_rate(
                overtime_type,
                detail.standard_working_hours,
            )

            overtime_amount = self.calculate_overtime_amount(
                overtime_type,
                hourly_rate,
                detail.overtime_duration,
                detail.date,
                holiday_date_map,
            )

            overtime_config = self.overtime_types[overtime_type]

            holiday_info = holiday_date_map.get(cstr(detail.date))

            if holiday_info:
                holiday_ot_hours += detail.overtime_duration

                salary_component = (
                    overtime_config.get(
                        "custom_holiday_overtime_salary_component"
                    )
                    or overtime_config["overtime_salary_component"]
                )
            else:
                peak_ot_hours += detail.overtime_duration

                salary_component = overtime_config["overtime_salary_component"]

            overtime_components[salary_component] = (
                overtime_components.get(salary_component, 0)
                + overtime_amount
            )

        # Store totals on Overtime Slip
        self.custom_total_peak_overtime_hours = peak_ot_hours
        self.custom_total_holiday_overtime_hours = holiday_ot_hours

        return overtime_components
    
    def _calculate_component_based_hourly_rate(
        self,
        overtime_type,
        standard_working_hours,
    ):
        components = self.overtime_types[overtime_type]["components"] or []

        if not hasattr(self, "_cached_salary_slip"):
            salary_structure = get_assigned_salary_structure(
                self.employee,
                self.start_date,
            )
            self._cached_salary_slip = self._make_salary_slip(
                salary_structure
            )

        if not components or not hasattr(self, "_cached_salary_slip"):
            return 0

        component_amount = sum(
            row.amount
            for row in self._cached_salary_slip.earnings
            if row.salary_component in components
            and not row.get("additional_salary")
        )

        payment_days = max(self._cached_salary_slip.payment_days, 1)
        applicable_daily_amount = component_amount / payment_days

        return (
            applicable_daily_amount / standard_working_hours
            if standard_working_hours
            else 0
        )