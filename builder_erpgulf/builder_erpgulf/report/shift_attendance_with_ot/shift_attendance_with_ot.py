# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from datetime import timedelta

import frappe
from frappe import _
from frappe.query_builder import Criterion
from frappe.utils import cint, flt, format_datetime, format_duration, getdate

from erpnext.accounts.utils import build_qb_match_conditions


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 220,
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": _("Employee Name"),
			"width": 0,
			"hidden": 1,
		},
		{
			"label": _("Shift"),
			"fieldname": "shift",
			"fieldtype": "Link",
			"options": "Shift Type",
			"width": 120,
		},
		{
			"label": _("Attendance Date"),
			"fieldname": "attendance_date",
			"fieldtype": "Date",
			"width": 130,
		},
		{
            "label": _("Day"),
            "fieldname": "day",
            "fieldtype": "Data",
            "width": 120,
        },
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _("Shift Start Time"),
			"fieldname": "shift_start",
			"fieldtype": "Data",
			"width": 125,
		},
		{
			"label": _("Shift End Time"),
			"fieldname": "shift_end",
			"fieldtype": "Data",
			"width": 125,
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
			"label": _("Total Working Hours"),
			"fieldname": "working_hours",
			"fieldtype": "Data",
			"width": 100,
		},
        {
            "label": _("Overtime Hours"),
            "fieldname": "overtime_hours",
            "fieldtype": "Data",
            "width": 120,
        },
		
		{
			"label": _("Late Entry By"),
			"fieldname": "late_entry_hrs",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Early Exit By"),
			"fieldname": "early_exit_hrs",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 150,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 150,
		},
		{
			"label": _("Shift Actual Start Time"),
			"fieldname": "shift_actual_start",
			"fieldtype": "Data",
			"width": 165,
		},
		{
			"label": _("Shift Actual End Time"),
			"fieldname": "shift_actual_end",
			"fieldtype": "Data",
			"width": 165,
		},
		{
			"label": _("Attendance ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Attendance",
			"width": 150,
		},
	]

def float_hours_to_hhmm(hours):
    if not hours:
        return ""

    total_minutes = int(round(flt(hours) * 60))
    hh = total_minutes // 60
    mm = total_minutes % 60
    return f"{hh:02d}:{mm:02d}"


def get_data(filters):
    data = get_attendance_with_checkins(filters)
    data = update_data(data, filters)

    if filters.include_attendance_without_checkins:
        data.extend(get_attendance_without_checkins(filters))

    for d in data:
        d.day = d.attendance_date.strftime("%A") if d.attendance_date else ""

    data = add_weekend_records(data, filters)

    for d in data:
        if d.status != "Weekend" and d.status not in ("Present", "Half Day"):

            if d.shift:
                shift = frappe.get_doc("Shift Type", d.shift)
                d.shift_start = shift.start_time if shift.get("start_time") else None
                d.shift_end = shift.end_time if shift.get("end_time") else None

            emp = frappe.get_doc("Employee", d.employee)
            d.department = emp.department
            d.company = emp.company

            d.in_time = None
            d.out_time = None
            d.working_hours = 0
            d.overtime_hours = 0
            d.late_entry_hrs = None
            d.early_exit_hrs = None

    total_overtime = 0
    employee = None
    company = None

    for d in data:
        total_overtime += flt(d.overtime_hours or 0)
        employee = employee or d.employee
        company = company or d.company

    for d in data:
        d.working_hours = float_hours_to_hhmm(d.working_hours)
        d.overtime_hours = float_hours_to_hhmm(d.overtime_hours)

    if total_overtime:
        data.append(frappe._dict({
            "employee": employee if filters.get("employee") else _("TOTAL"),
            "employee_name": "",
            "shift": None,
            "attendance_date": None,
            "day": "",
            "status": "",
            "shift_start": None,
            "shift_end": None,
            "in_time": None,
            "out_time": None,
            "working_hours": None,
            "overtime_hours": float_hours_to_hhmm(total_overtime),
            "late_entry": None,
            "late_entry_hrs": None,
            "early_exit": None,
            "early_exit_hrs": None,
            "department": None,
            "company": company,
            "shift_actual_start": None,
            "shift_actual_end": None,
            "name": None,
        }))

    return data

def add_weekend_records(data, filters):
    from datetime import timedelta
    from frappe.utils import getdate

    employee_shift_map = {d.employee: d.shift for d in data}
    employees = set(employee_shift_map.keys())

    shift_holiday_map = {}
    shift_types = frappe.get_all(
        "Shift Type",
        fields=["name", "holiday_list"],
        filters={"name": ["in", list(employee_shift_map.values())]},
    )
    for st in shift_types:
        shift_holiday_map[st["name"]] = st.get("holiday_list")

    last_attendance_map = {}
    for d in data:
        if d.attendance_date:
            last_attendance_map[d.employee] = max(d.attendance_date, last_attendance_map.get(d.employee, d.attendance_date))

    existing_attendance = set((d.employee, d.attendance_date) for d in data if d.attendance_date)

    start_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))

    for emp in employees:
        emp_shift = employee_shift_map.get(emp)
        holiday_list_name = shift_holiday_map.get(emp_shift)
        if not holiday_list_name:
            continue

        end_date_for_emp = min(to_date, last_attendance_map.get(emp, to_date))

        holidays = frappe.get_all(
            "Holiday",
            fields=["holiday_date"],
            filters={
                "parent": holiday_list_name,
                "holiday_date": ["between", [start_date, end_date_for_emp]]
            }
        )
        holiday_dates = set([h["holiday_date"] for h in holidays])

        for hdate in holiday_dates:
            if (emp, hdate) not in existing_attendance:
                data.append(frappe._dict({
                    "employee": emp,
                    "employee_name": frappe.db.get_value("Employee", emp, "employee_name"),
                    "shift": emp_shift,
                    "attendance_date": hdate,
                    "day": hdate.strftime("%A"),
                    "status": "Weekend",
                    "shift_start": None,
                    "shift_end": None,
                    "in_time": None,
                    "out_time": None,
                    "working_hours": 0,
                    "overtime_hours": 0,
                    "late_entry": 0,
                    "late_entry_hrs": None,
                    "early_exit": 0,
                    "early_exit_hrs": None,
                    "department": frappe.db.get_value("Employee", emp, "department"),
                    "company": frappe.db.get_value("Employee", emp, "company"),
                    "shift_actual_start": None,
                    "shift_actual_end": None,
                    "name": None
                }))

    return data


def get_report_summary(data):
    if not data:
        return None

    present_records = half_day_records = absent_records = late_entries = early_exits = 0

    for entry in data:
        if not entry.attendance_date:
            continue

        if entry.status == "Present":
            present_records += 1
        elif entry.status == "Half Day":
            half_day_records += 1
        elif entry.status == "Absent":
            absent_records += 1

        if entry.late_entry:
            late_entries += 1
        if entry.early_exit:
            early_exits += 1

    return [
        {
            "value": present_records,
            "indicator": "Green",
            "label": _("Present Records"),
            "datatype": "Int",
        },
        {
            "value": half_day_records,
            "indicator": "Blue",
            "label": _("Half Day Records"),
            "datatype": "Int",
        },
        {
            "value": absent_records,
            "indicator": "Red",
            "label": _("Absent Records"),
            "datatype": "Int",
        },
        {
            "value": late_entries,
            "indicator": "Red",
            "label": _("Late Entries"),
            "datatype": "Int",
        },
        {
            "value": early_exits,
            "indicator": "Red",
            "label": _("Early Exits"),
            "datatype": "Int",
        },
    ]


def get_chart_data(data):
	if not data:
		return None

	total_shift_records = {}
	for entry in data:
		total_shift_records.setdefault(entry.shift, 0)
		total_shift_records[entry.shift] += 1

	labels = [_(d) for d in list(total_shift_records)]
	chart = {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Shift"), "values": list(total_shift_records.values())}],
		},
		"type": "percentage",
	}
	return chart


def get_attendance_with_checkins(filters):
	attendance = frappe.qb.DocType("Attendance")
	checkin = frappe.qb.DocType("Employee Checkin")
	shift_type = frappe.qb.DocType("Shift Type")

	query = (
		get_base_attendance_query(filters)
		.inner_join(checkin)
		.on(checkin.attendance == attendance.name)
		.select(
			checkin.shift_start,
			checkin.shift_end,
			checkin.shift_actual_start,
			checkin.shift_actual_end,
			shift_type.enable_late_entry_marking,
			shift_type.late_entry_grace_period,
			shift_type.enable_early_exit_marking,
			shift_type.early_exit_grace_period,
		)
	)
	for field in filters:
		if field == "late_entry" and not filters.consider_grace_period:
			query = query.where(attendance.in_time > checkin.shift_start)
		elif field == "early_exit" and not filters.consider_grace_period:
			query = query.where(attendance.out_time < checkin.shift_end)
	result = query.run(as_dict=True)
	return result


def get_base_attendance_query(filters):
	attendance = frappe.qb.DocType("Attendance")
	shift_type = frappe.qb.DocType("Shift Type")

	query = (
		frappe.qb.from_(attendance)
		.inner_join(shift_type)
		.on(attendance.shift == shift_type.name)
		.select(
			attendance.name,
			attendance.employee,
			attendance.employee_name,
			attendance.shift,
			attendance.attendance_date,
			attendance.status,
			attendance.in_time,
			attendance.out_time,
			attendance.working_hours,
            attendance.overtime_hours,
			attendance.late_entry,
			attendance.early_exit,
			attendance.department,
			attendance.company,
		)
		.where(attendance.docstatus == 1)
		.groupby(attendance.name)
	)

	for field in filters:
		if field == "from_date":
			query = query.where(attendance.attendance_date >= filters.from_date)
		elif field == "to_date":
			query = query.where(attendance.attendance_date <= filters.to_date)
		elif field in ["consider_grace_period", "include_attendance_without_checkins"]:
			continue
		else:
			query = query.where(attendance[field] == filters[field])

	query = query.where(Criterion.all(build_qb_match_conditions("Attendance")))
	return query


def get_attendance_without_checkins(filters):
	attendance = frappe.qb.DocType("Attendance")
	checkin = frappe.qb.DocType("Employee Checkin")

	query = (
		get_base_attendance_query(filters)
		.left_join(checkin)
		.on(checkin.attendance == attendance.name)
		.where(checkin.attendance.isnull())
	)
	result = query.run(as_dict=True)
	return result


def update_data(data, filters):
	for d in data:
		update_late_entry(d, filters.consider_grace_period)
		update_early_exit(d, filters.consider_grace_period)

		d.working_hours = format_float_precision(d.working_hours)
		d.overtime_hours = format_float_precision(d.overtime_hours)

		d.in_time, d.out_time = format_in_out_time(d.in_time, d.out_time, d.attendance_date)
		d.shift_start, d.shift_end = convert_datetime_to_time_for_same_date(d.shift_start, d.shift_end)
		d.shift_actual_start, d.shift_actual_end = convert_datetime_to_time_for_same_date(
			d.shift_actual_start, d.shift_actual_end
		)

	return data


def format_float_precision(value):
	precision = cint(frappe.db.get_default("float_precision")) or 2
	return flt(value, precision)


def format_in_out_time(in_time, out_time, attendance_date):
	if in_time and not out_time and in_time.date() == attendance_date:
		in_time = in_time.time()
	elif out_time and not in_time and out_time.date() == attendance_date:
		out_time = out_time.time()
	else:
		in_time, out_time = convert_datetime_to_time_for_same_date(in_time, out_time)
	return in_time, out_time


def convert_datetime_to_time_for_same_date(start, end):
	if start and end and start.date() == end.date():
		start = start.time()
		end = end.time()
	else:
		start = format_datetime(start)
		end = format_datetime(end)
	return start, end


def update_late_entry(entry, consider_grace_period):
	if consider_grace_period:
		if entry.late_entry:
			entry_grace_period = entry.late_entry_grace_period if entry.enable_late_entry_marking else 0
			start_time = entry.shift_start + timedelta(minutes=entry_grace_period)
			entry.late_entry_hrs = entry.in_time - start_time
	elif entry.in_time and entry.in_time > entry.shift_start:
		entry.late_entry = 1
		entry.late_entry_hrs = entry.in_time - entry.shift_start
	if entry.late_entry_hrs:
		entry.late_entry_hrs = format_duration(entry.late_entry_hrs.total_seconds())


def update_early_exit(entry, consider_grace_period):
	if consider_grace_period:
		if entry.early_exit:
			exit_grace_period = entry.early_exit_grace_period if entry.enable_early_exit_marking else 0
			end_time = entry.shift_end - timedelta(minutes=exit_grace_period)
			entry.early_exit_hrs = end_time - entry.out_time
	elif entry.out_time and entry.out_time < entry.shift_end:
		entry.early_exit = 1
		entry.early_exit_hrs = entry.shift_end - entry.out_time
	if entry.early_exit_hrs:
		entry.early_exit_hrs = format_duration(entry.early_exit_hrs.total_seconds())