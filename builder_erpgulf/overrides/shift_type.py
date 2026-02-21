from datetime import datetime
import frappe
from frappe.utils import getdate, get_datetime
from hrms.hr.doctype.shift_type.shift_type import ShiftType
from hrms.hr.doctype.shift_assignment.shift_assignment import (
    get_employee_shift,
    get_shift_details
)

class SameDayAbsentShiftType(ShiftType):

    def get_start_and_end_dates(self, employee):
        """
        SAME-DAY absent override
        Removes the 1-day buffer used by ERPNext
        """

        date_of_joining, relieving_date, employee_creation = frappe.get_cached_value(
            "Employee",
            employee,
            ["date_of_joining", "relieving_date", "creation"],
        )

        if not date_of_joining:
            date_of_joining = employee_creation.date()

        start_date = max(getdate(self.process_attendance_after), date_of_joining)
        end_date = None

        shift_details = get_shift_details(
            self.name,
            get_datetime(self.last_sync_of_checkin),
        )

        last_shift_time = (
            shift_details.actual_end
            if shift_details
            else get_datetime(self.last_sync_of_checkin)
        )

        prev_shift = get_employee_shift(
            employee,
            last_shift_time,
            True,
            "reverse",
        )

        if prev_shift and prev_shift.shift_type.name == self.name:
            end_date = (
                min(prev_shift.start_datetime.date(), relieving_date)
                if relieving_date
                else prev_shift.start_datetime.date()
            )
        else:
            return None, None

        return start_date, end_date
