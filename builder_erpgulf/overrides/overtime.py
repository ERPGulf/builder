import frappe
from hrms.hr.doctype.attendance.attendance import Attendance as HRMSAttendance
from frappe.utils import get_datetime, time_diff_in_hours


class Attendance(HRMSAttendance):

    def validate(self):
        super().validate()
        self.calculate_overtime_hours()

    def calculate_overtime_hours(self):
        self.overtime_hours = 0

        if not (self.shift and self.in_time and self.out_time):
            return

        shift = frappe.get_doc("Shift Type", self.shift)

        if not shift.enable_overtime_calculation:
            return

        attendance_date = get_datetime(self.attendance_date)

        shift_start = attendance_date.replace(
            hour=int(shift.start_time.total_seconds() // 3600),
            minute=int((shift.start_time.total_seconds() % 3600) // 60),
            second=0
        )

        shift_end = attendance_date.replace(
            hour=int(shift.end_time.total_seconds() // 3600),
            minute=int((shift.end_time.total_seconds() % 3600) // 60),
            second=0
        )

        if shift_end <= shift_start:
            shift_end = frappe.utils.add_days(shift_end, 1)

        shift_hours = time_diff_in_hours(shift_end, shift_start)

        working_hours = time_diff_in_hours(self.out_time, self.in_time)

        if working_hours > shift_hours:
            self.overtime_hours = round(working_hours - shift_hours, 2)
        else:
            self.overtime_hours = 0

	