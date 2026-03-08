from datetime import timedelta

import frappe
from frappe import _
from frappe.query_builder import Criterion
from frappe.utils import cint, flt, format_datetime, format_duration, formatdate, getdate, add_days

from erpnext.accounts.utils import build_qb_match_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


# -------------------------------------------------------------
# Columns
# -------------------------------------------------------------

def get_columns():
	return [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 200,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Attendance Date"),
			"fieldname": "attendance_date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Day"),
			"fieldname": "day",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Shift"),
			"fieldname": "shift",
			"fieldtype": "Link",
			"options": "Shift Type",
			"width": 150,
		},
		{
			"label": _("In Time"),
			"fieldname": "in_time",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Out Time"),
			"fieldname": "out_time",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Working Hours"),
			"fieldname": "working_hours",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Overtime Hours"),
			"fieldname": "overtime_hours",
			"fieldtype": "Float",
			"width": 120,
		},
	]


# -------------------------------------------------------------
# Main Data Builder
# -------------------------------------------------------------

def get_data(filters):

	attendance_data = get_attendance_records(filters)

	all_dates = get_all_dates(filters.from_date, filters.to_date)

	employees = get_employees(filters)

	final_data = []

	for emp in employees:

		holiday_list = frappe.db.get_value("Employee", emp.name, "holiday_list")

		emp_attendance = {
			d.attendance_date: d for d in attendance_data if d.employee == emp.name
		}

		for dt in all_dates:

			if dt in emp_attendance:
				row = emp_attendance[dt]
			else:

				status = get_day_status(holiday_list, dt)

				row = frappe._dict(
					employee=emp.name,
					employee_name=emp.employee_name,
					attendance_date=dt,
					day=formatdate(dt, "EEEE"),
					status=status,
				)

			row.day = formatdate(dt, "EEEE")

			final_data.append(row)

	return sorted(final_data, key=lambda x: (x.employee, x.attendance_date))


# -------------------------------------------------------------
# Attendance Query
# -------------------------------------------------------------

def get_attendance_records(filters):

	attendance = frappe.qb.DocType("Attendance")

	query = (
		frappe.qb.from_(attendance)
		.select(
			attendance.name,
			attendance.employee,
			attendance.employee_name,
			attendance.attendance_date,
			attendance.status,
			attendance.shift,
			attendance.in_time,
			attendance.out_time,
			attendance.working_hours,
			attendance.overtime_hours,
		)
		.where(attendance.docstatus == 1)
	)

	if filters.get("employee"):
		query = query.where(attendance.employee == filters.employee)

	if filters.get("company"):
		query = query.where(attendance.company == filters.company)

	if filters.get("from_date"):
		query = query.where(attendance.attendance_date >= filters.from_date)

	if filters.get("to_date"):
		query = query.where(attendance.attendance_date <= filters.to_date)

	return query.run(as_dict=True)


# -------------------------------------------------------------
# Employees
# -------------------------------------------------------------

def get_employees(filters):

	return frappe.get_all(
		"Employee",
		fields=["name", "employee_name"],
		filters={"status": "Active", "company": filters.company},
	)


# -------------------------------------------------------------
# Date Range
# -------------------------------------------------------------

def get_all_dates(from_date, to_date):

	dates = []

	current = getdate(from_date)

	while current <= getdate(to_date):
		dates.append(current)
		current = add_days(current, 1)

	return dates


# -------------------------------------------------------------
# Holiday / Weekend Detection
# -------------------------------------------------------------

def get_day_status(holiday_list, date):

	if is_holiday(holiday_list, date):
		return "Holiday"

	weekday = date.weekday()

	if weekday in [5, 6]:
		return "Weekend"

	return "Absent"


def is_holiday(holiday_list, date):

	if not holiday_list:
		return False

	return frappe.db.exists(
		"Holiday",
		{
			"parent": holiday_list,
			"holiday_date": date,
		},
	)