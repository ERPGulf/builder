# Copyright (c) 2025, ERPGulf and contributors
# For license information, please see license.txt

# import frappe


import frappe

def execute(filters=None):
    columns = [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 180},
        {"label": "Planned Value (PV)", "fieldname": "pv", "fieldtype": "Currency", "width": 150},
        {"label": "Earned Value (EV)", "fieldname": "ev", "fieldtype": "Currency", "width": 150},
        {"label": "Actual Cost (AC)", "fieldname": "ac", "fieldtype": "Currency", "width": 150},
        {"label": "Schedule Variance (SV)", "fieldname": "sv", "fieldtype": "Float", "width": 160},
        {"label": "SV Status", "fieldname": "sv_status", "fieldtype": "Data", "width": 160},
        {"label": "Milestones Completed", "fieldname": "milestones", "fieldtype": "Int", "width": 150},
        {"label": "Overall Progress (%)", "fieldname": "progress", "fieldtype": "Percent", "width": 150},
    ]

    projects = frappe.get_all(
        "Project",
        fields=[
            "name",
            "custom_planned_value",
            "custom_earned_value",
            "custom_actual_cost",
            "custom_schedule_variance",
            "custom_sv_status",
            "percent_complete"
        ]
    )

    data = []
    for p in projects:
        # milestones count
        milestone_count = frappe.db.count(
            "Project Milestone",
            {"project": p.name, "milestone_status": "Completed"}
        )

        data.append({
            "project": p.name,
            "pv": p.custom_planned_value,
            "ev": p.custom_earned_value,
            "ac": p.custom_actual_cost,
            "sv": p.custom_schedule_variance,
            "sv_status": p.custom_sv_status,
            "milestones": milestone_count,
            "progress": p.percent_complete
        })

    return columns, data

