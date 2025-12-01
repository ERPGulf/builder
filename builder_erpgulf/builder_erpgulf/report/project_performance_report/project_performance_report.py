# Copyright (c) 2025, ERPGulf and contributors
# For license information, please see license.txt

# import frappe


import frappe

def execute(filters=None):
    columns = [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 180},
        {"label": "CPI", "fieldname": "cpi", "fieldtype": "Float", "width": 120},
        {"label": "CPI Status", "fieldname": "cpi_status", "fieldtype": "Data", "width": 150},
        {"label": "Schedule Variance", "fieldname": "sv", "fieldtype": "Float", "width": 150},
        {"label": "SV Status", "fieldname": "sv_status", "fieldtype": "Data", "width": 150},
        {"label": "Cost Variance (CV)", "fieldname": "cv", "fieldtype": "Float", "width": 160},
        {"label": "CV Status", "fieldname": "cv_status", "fieldtype": "Data", "width": 140},
        {"label": "Risk Count", "fieldname": "risk_count", "fieldtype": "Int", "width": 120},
        {"label": "Stakeholders", "fieldname": "stakeholders", "fieldtype": "Int", "width": 120},
    ]

    projects = frappe.get_all(
        "Project",
        fields=[
            "name",
            "custom_cost_performance_index",
            "custom_cpi_status",
            "custom_schedule_variance",
            "custom_sv_status",
            "custom_cost_variance",
            "custom_cv_status"
        ]
    )

    data = []

    for p in projects:
        # risk register count
        risk_count = frappe.db.count("Project Risk Register", {"project": p.name})
        

        # stakeholder count
        stakeholders = frappe.db.count("Project Stakeholder", {"project": p.name})

        data.append({
            "project": p.name,
            "cpi": p.custom_cost_performance_index,
            "cpi_status": p.custom_cpi_status,
            "sv": p.custom_schedule_variance,
            "sv_status": p.custom_sv_status,
            "cv": p.custom_cost_variance,
            "cv_status": p.custom_cv_status,
            "risk_count": risk_count,
            "stakeholders": stakeholders
        })

    return columns, data

