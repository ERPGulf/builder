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

    in_time = get_datetime(self.in_time)
    out_time = get_datetime(self.out_time)

    attendance_date = get_datetime(self.attendance_date)

    start_seconds = shift.start_time.total_seconds()
    end_seconds = shift.end_time.total_seconds()

    start_hour = int(start_seconds // 3600)
    start_min = int((start_seconds % 3600) // 60)

    end_hour = int(end_seconds // 3600)
    end_min = int((end_seconds % 3600) // 60)

    shift_start = attendance_date.replace(
        hour=start_hour,
        minute=start_min,
        second=0,
        microsecond=0
    )

    shift_end = attendance_date.replace(
        hour=end_hour,
        minute=end_min,
        second=0,
        microsecond=0
    )

    if shift_end <= shift_start:
        shift_end = frappe.utils.add_days(shift_end, 1)

    overtime = 0

    if in_time < shift_start:
        overtime += time_diff_in_hours(shift_start, in_time)

    if out_time > shift_end:
        overtime += time_diff_in_hours(out_time, shift_end)

    self.overtime_hours = round(overtime, 2)

	# def calculate_overtime_hours(self):

	# 	self.overtime_hours = 0

	# 	if not (self.shift and self.in_time and self.out_time):
	# 		return

	# 	shift = frappe.get_doc("Shift Type", self.shift)

	# 	if not shift.enable_overtime_calculation:
	# 		return

	# 	attendance_date = get_datetime(self.attendance_date)

	# 	start_seconds = shift.start_time.total_seconds()
	# 	end_seconds = shift.end_time.total_seconds()

	# 	start_hour = int(start_seconds // 3600)
	# 	start_min = int((start_seconds % 3600) // 60)

	# 	end_hour = int(end_seconds // 3600)
	# 	end_min = int((end_seconds % 3600) // 60)

	# 	shift_start = attendance_date.replace(
	# 		hour=start_hour,
	# 		minute=start_min,
	# 		second=0
	# 	)

	# 	shift_end = attendance_date.replace(
	# 		hour=end_hour,
	# 		minute=end_min,
	# 		second=0
	# 	)

	# 	overtime = 0

	# 	if self.in_time < shift_start:
	# 		overtime += time_diff_in_hours(shift_start, self.in_time)

	# 	if self.out_time > shift_end:
	# 		overtime += time_diff_in_hours(self.out_time, shift_end)

	# 	self.overtime_hours = round(overtime, 2)