import frappe
from hrms.hr.doctype.attendance.attendance import Attendance as HRMSAttendance
from frappe.utils import time_diff_in_hours


class Attendance(HRMSAttendance):
	def validate(self):
		super().validate()
		self.calculate_overtime_hours()

	def calculate_overtime_hours(self):
		self.overtime_hours = 0

		if not self.working_hours:
			return

		if self.status in ("Absent", "On Leave"):
			return

		shift_hours = 0

		if self.shift:
			shift = frappe.db.get_value(
				"Shift Type",
				self.shift,
				["start_time", "end_time"],
				as_dict=True,
			)

			if shift and shift.start_time and shift.end_time:
				shift_hours = time_diff_in_hours(
					shift.end_time,
					shift.start_time
				)

		if not shift_hours and self.standard_working_hours:
			shift_hours = self.standard_working_hours

		if self.working_hours > shift_hours:
			self.overtime_hours = round(
				self.working_hours - shift_hours, 2
			)