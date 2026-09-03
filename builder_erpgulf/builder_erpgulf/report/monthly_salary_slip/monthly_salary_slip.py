# Copyright (c) 2026, ERPGulf and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

import erpnext


def execute(filters=None):
	if not filters:
		filters = {}

	currency = filters.get("currency")
	company = filters.get("company")

	if not company:
		return [], []

	company_currency = erpnext.get_company_currency(company)

	salary_slips = get_salary_slips(filters, company_currency)

	if not salary_slips:
		return get_empty_columns(), []

	# ---------------------------------------------------------
	# 1. Get Salary Structure components
	# ---------------------------------------------------------
	structure_components = get_salary_structure_components(salary_slips)

	# ---------------------------------------------------------
	# 2. Get actual Salary Slip component amounts
	# ---------------------------------------------------------
	ss_component_map = get_salary_slip_details(
		salary_slips,
		currency,
		company_currency,
	)

	# ---------------------------------------------------------
	# 3. Get Additional Salary components
	# ---------------------------------------------------------
	additional_salary_map = get_additional_salary_details(
		salary_slips,
		filters,
	)

	additional_components = get_additional_salary_components(
		additional_salary_map
	)

	# ---------------------------------------------------------
	# 4. Employee Date of Joining
	# ---------------------------------------------------------
	doj_map = get_employee_doj_map()

	# ---------------------------------------------------------
	# 5. Create columns
	# ---------------------------------------------------------
	columns = get_columns(
		structure_components,
		additional_components,
	)

	# ---------------------------------------------------------
	# 6. Create data
	# ---------------------------------------------------------
	data = []

	for ss in salary_slips:

		row = {
			"salary_slip_id": ss.name,
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"date_of_joining": doj_map.get(ss.employee),
			"branch": ss.branch,
			"department": ss.department,
			"designation": ss.designation,
			"company": ss.company,
			"start_date": ss.start_date,
			"end_date": ss.end_date,
			"leave_without_pay": ss.leave_without_pay,
			"absent_days": ss.absent_days,
			"payment_days": ss.payment_days,
			"currency": currency or company_currency,
			"total_loan_repayment": getattr(
				ss,
				"total_loan_repayment",
				0,
			),
		}

		# -----------------------------------------------------
		# Salary Structure component amounts
		# -----------------------------------------------------
		ss_components = ss_component_map.get(ss.name, {})

		for component in structure_components:
			fieldname = get_component_fieldname(
				"structure",
				component,
			)

			row[fieldname] = flt(
				ss_components.get(component, 0)
			)

		# -----------------------------------------------------
		# Gross Pay
		# -----------------------------------------------------
		if currency == company_currency:
			row["gross_pay"] = (
				flt(ss.gross_pay)
				* flt(ss.exchange_rate or 1)
			)
		else:
			row["gross_pay"] = flt(ss.gross_pay)

		# -----------------------------------------------------
		# Additional Salary component amounts
		# -----------------------------------------------------
		employee_additional = additional_salary_map.get(
			ss.employee,
			{},
		)

		for component in additional_components:
			fieldname = get_component_fieldname(
				"additional",
				component,
			)

			row[fieldname] = flt(
				employee_additional.get(component, 0)
			)

		# -----------------------------------------------------
		# Total Deduction / Net Pay
		# -----------------------------------------------------
		if currency == company_currency:
			row["total_deduction"] = (
				flt(ss.total_deduction)
				+ flt(getattr(ss, "total_loan_repayment", 0))
			) * flt(ss.exchange_rate or 1)

			row["net_pay"] = (
				flt(ss.net_pay)
				* flt(ss.exchange_rate or 1)
			)

		else:
			row["total_deduction"] = (
				flt(ss.total_deduction)
				+ flt(getattr(ss, "total_loan_repayment", 0))
			)

			row["net_pay"] = flt(ss.net_pay)

		data.append(row)

	return columns, data


# =============================================================
# Salary Slips
# =============================================================

def get_salary_slips(filters, company_currency):

	doc_status = {
		"Draft": 0,
		"Submitted": 1,
		"Cancelled": 2,
	}

	salary_slip = frappe.qb.DocType("Salary Slip")

	query = (
		frappe.qb
		.from_(salary_slip)
		.select(salary_slip.star)
	)

	if filters.get("docstatus"):
		query = query.where(
			salary_slip.docstatus
			== doc_status[filters.get("docstatus")]
		)

	if filters.get("from_date"):
		query = query.where(
			salary_slip.start_date
			>= filters.get("from_date")
		)

	if filters.get("to_date"):
		query = query.where(
			salary_slip.end_date
			<= filters.get("to_date")
		)

	if filters.get("company"):
		query = query.where(
			salary_slip.company
			== filters.get("company")
		)

	if filters.get("employee"):
		query = query.where(
			salary_slip.employee
			== filters.get("employee")
		)

	if (
		filters.get("currency")
		and filters.get("currency") != company_currency
	):
		query = query.where(
			salary_slip.currency
			== filters.get("currency")
		)

	if filters.get("department"):
		query = query.where(
			salary_slip.department
			== filters.get("department")
		)

	if filters.get("designation"):
		query = query.where(
			salary_slip.designation
			== filters.get("designation")
		)

	if filters.get("branch"):
		query = query.where(
			salary_slip.branch
			== filters.get("branch")
		)

	return query.run(as_dict=True) or []


# =============================================================
# Salary Structure Components
# =============================================================

def get_salary_structure_components(salary_slips):

	"""
	Get all Earnings and Deductions defined in the Salary Structure
	used by the Salary Slip.

	The Salary Slip's salary_structure is used first because this
	represents the structure actually used to generate that slip.
	"""

	structure_names = {
		ss.salary_structure
		for ss in salary_slips
		if getattr(ss, "salary_structure", None)
	}

	# Fallback to Salary Structure Assignment if salary_structure
	# is not available on Salary Slip.
	if not structure_names:

		employees = {
			ss.employee
			for ss in salary_slips
			if ss.employee
		}

		structure_names = set()

		for employee in employees:

			assignment = frappe.db.get_value(
				"Salary Structure Assignment",
				{
					"employee": employee,
					"docstatus": 1,
				},
				"salary_structure",
				order_by="from_date desc",
			)

			if assignment:
				structure_names.add(assignment)

	if not structure_names:
		return []

	components = []

	for structure_name in structure_names:

		# Earnings
		earnings = frappe.get_all(
			"Salary Detail",
			filters={
				"parent": structure_name,
				"parenttype": "Salary Structure",
				"parentfield": "earnings",
			},
			fields=[
				"salary_component",
			],
			order_by="idx asc",
		)

		# Deductions
		deductions = frappe.get_all(
			"Salary Detail",
			filters={
				"parent": structure_name,
				"parenttype": "Salary Structure",
				"parentfield": "deductions",
			},
			fields=[
				"salary_component",
			],
			order_by="idx asc",
		)

		for row in earnings + deductions:

			component = row.salary_component

			if component and component not in components:
				components.append(component)

	return components


# =============================================================
# Salary Slip component amounts
# =============================================================

def get_salary_slip_details(
	salary_slips,
	currency,
	company_currency,
):

	salary_slip = frappe.qb.DocType("Salary Slip")
	salary_detail = frappe.qb.DocType("Salary Detail")

	slip_names = [
		ss.name
		for ss in salary_slips
	]

	if not slip_names:
		return {}

	result = (
		frappe.qb
		.from_(salary_slip)
		.join(salary_detail)
		.on(
			salary_slip.name
			== salary_detail.parent
		)
		.where(
			(salary_detail.parent.isin(slip_names))
			& (
				salary_detail.parentfield.isin(
					[
						"earnings",
						"deductions",
					]
				)
			)
		)
		.select(
			salary_detail.parent,
			salary_detail.salary_component,
			salary_detail.amount,
			salary_slip.exchange_rate,
		)
	).run(as_dict=True)

	result_map = {}

	for row in result:

		result_map.setdefault(
			row.parent,
			{},
		)

		amount = flt(row.amount)

		if currency == company_currency:
			amount *= flt(
				row.exchange_rate or 1
			)

		result_map[row.parent].setdefault(
			row.salary_component,
			0,
		)

		result_map[row.parent][
			row.salary_component
		] += amount

	return result_map


# =============================================================
# Additional Salary
# =============================================================

def get_additional_salary_details(
	salary_slips,
	filters,
):

	"""
	Get submitted Additional Salary records for the employee
	and the selected salary period.

	The date is based on Additional Salary.payroll_date.
	"""

	employees = {
		ss.employee
		for ss in salary_slips
		if ss.employee
	}

	if not employees:
		return {}

	additional_salary = frappe.qb.DocType(
		"Additional Salary"
	)

	query = (
		frappe.qb
		.from_(additional_salary)
		.select(
			additional_salary.employee,
			additional_salary.salary_component,
			additional_salary.amount,
			additional_salary.payroll_date,
		)
		.where(
			additional_salary.employee.isin(
				list(employees)
			)
		)
		.where(
			additional_salary.docstatus == 1
		)
	)

	if filters.get("from_date"):
		query = query.where(
			additional_salary.payroll_date
			>= filters.get("from_date")
		)

	if filters.get("to_date"):
		query = query.where(
			additional_salary.payroll_date
			<= filters.get("to_date")
		)

	result = query.run(as_dict=True)

	result_map = {}

	for row in result:

		result_map.setdefault(
			row.employee,
			{},
		)

		result_map[row.employee].setdefault(
			row.salary_component,
			0,
		)

		result_map[row.employee][
			row.salary_component
		] += flt(row.amount)

	return result_map


def get_additional_salary_components(
	additional_salary_map,
):

	components = []

	for employee_data in additional_salary_map.values():

		for component in employee_data:

			if component not in components:
				components.append(component)

	return sorted(components)


# =============================================================
# Employee
# =============================================================

def get_employee_doj_map():

	employee = frappe.qb.DocType("Employee")

	result = (
		frappe.qb
		.from_(employee)
		.select(
			employee.name,
			employee.date_of_joining,
		)
	).run()

	return frappe._dict(result)


# =============================================================
# Columns
# =============================================================

def get_columns(
	structure_components,
	additional_components,
):

	columns = [

		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 150,
		},

		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},

		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},

		{
			"label": _("Date of Joining"),
			"fieldname": "date_of_joining",
			"fieldtype": "Date",
			"width": 100,
		},

		{
			"label": _("Branch"),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 120,
		},

		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 120,
		},

		{
			"label": _("Designation"),
			"fieldname": "designation",
			"fieldtype": "Link",
			"options": "Designation",
			"width": 120,
		},

		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120,
		},

		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 90,
		},

		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 90,
		},

		{
			"label": _("Leave Without Pay"),
			"fieldname": "leave_without_pay",
			"fieldtype": "Float",
			"width": 100,
		},

		{
			"label": _("Absent Days"),
			"fieldname": "absent_days",
			"fieldtype": "Float",
			"width": 100,
		},

		{
			"label": _("Payment Days"),
			"fieldname": "payment_days",
			"fieldtype": "Float",
			"width": 100,
		},

	]

	# ---------------------------------------------------------
	# Salary Structure components
	# ---------------------------------------------------------

	for component in structure_components:

		columns.append(
			{
				"label": component,
				"fieldname": get_component_fieldname(
					"structure",
					component,
				),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	# ---------------------------------------------------------
	# Gross Pay
	# ---------------------------------------------------------

	columns.append(
		{
			"label": _("Gross Pay"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
	)

	# ---------------------------------------------------------
	# Additional Salary components
	# ---------------------------------------------------------

	for component in additional_components:

		columns.append(
			{
				"label": _("Additional - {0}").format(
					component
				),
				"fieldname": get_component_fieldname(
					"additional",
					component,
				),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 140,
			}
		)

	# ---------------------------------------------------------
	# Totals
	# ---------------------------------------------------------

	columns.extend(
		[
			{
				"label": _("Total Loan Repayment"),
				"fieldname": "total_loan_repayment",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Total Deduction"),
				"fieldname": "total_deduction",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Net Pay"),
				"fieldname": "net_pay",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Currency"),
				"fieldname": "currency",
				"fieldtype": "Data",
				"hidden": 1,
			},
		]
	)

	return columns


# =============================================================
# Fieldname helper
# =============================================================

def get_component_fieldname(
	prefix,
	component,
):

	return frappe.scrub(
		f"{prefix}_{component}"
	)


# =============================================================
# Empty report
# =============================================================

def get_empty_columns():

	return [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 150,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
	]