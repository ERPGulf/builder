
import frappe
from frappe.utils import getdate, today

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Act #", "fieldname": "idx", "fieldtype": "Data", "width": 60},
        {"label": "Act. Description", "fieldname": "subject", "fieldtype": "Data", "width": 250},
        {"label": "Area", "fieldname": "area", "fieldtype": "Data", "width": 120},
        {"label": "Date Started", "fieldname": "start_date", "fieldtype": "Date", "width": 120},
        {"label": "Date Completed", "fieldname": "end_date", "fieldtype": "Date", "width": 120},
        {"label": "% Comp.", "fieldname": "progress", "fieldtype": "Data", "width": 90},
        {"label": "Remarks", "fieldname": "description", "fieldtype": "Data", "width": 250},
    ]


def get_data(filters):
    project = filters.get("project")
    if not project:
        return []

    today_date = getdate(today())

    parents = frappe.db.get_all(
        "Task",
        filters={
            "project": project,
            "is_group": 1
        },
        fields=[
            "name",
            "subject",
            "exp_start_date",
            "exp_end_date",
            "progress",
            "description"
        ],
        order_by="creation asc"
    )

    data = []

    # -------------------------------
    # TABLE 1 → Activities in Progress
    # -------------------------------
    data.append({"subject": "Activities in Progress", "idx": "", "is_section": 1})

    activities_in_progress = []

    for parent in parents:
        children = frappe.db.get_all(
            "Task",
            filters={
                "project": project,
                "parent_task": parent.name
            },
            fields=[
                "name",
                "subject",
                "exp_start_date",
                "exp_end_date",
                "progress",
                "description"
            ],
            order_by="creation asc"
        )

        activities_in_progress.append({
            "parent": parent,
            "children": children
        })

    for section in activities_in_progress:
        p = section["parent"]

        # Parent Row (FULL)
        data.append({
            "idx": "",
            "subject": p.subject,
            "start_date": p.exp_start_date,
            "end_date": p.exp_end_date,
            "progress": f"{p.progress or 0}%",
            "description": p.description,
            "indent": 0,
            "is_bold": 1
        })

        for i, task in enumerate(section["children"], start=1):
            data.append({
                "idx": i,
                "subject": task.subject,
                "start_date": task.exp_start_date,
                "end_date": task.exp_end_date,
                "progress": f"{task.progress or 0}%",
                "description": task.description,
                "indent": 1
            })

    # -------------------------------
    # TABLE 2 → Activities Planned Next Day
    # -------------------------------
    data.append({"subject": "", "idx": ""})  # spacer
    data.append({"subject": "Activities Planned for the Next Day", "idx": "", "is_section": 1})

    activities_next_day = []

    for parent in parents:
        children = frappe.db.get_all(
            "Task",
            filters={
                "project": project,
                "parent_task": parent.name
            },
            fields=[
                "name",
                "subject",
                "exp_start_date",
                "exp_end_date",
                "progress",
                "description"
            ],
            order_by="creation asc"
        )

        future_children = [
            c for c in children
            if c.exp_start_date and getdate(c.exp_start_date) > today_date
        ]

        if future_children:
            activities_next_day.append({
                "parent": parent,
                "children": future_children
            })

    for section in activities_next_day:
        p = section["parent"]

        # Parent Row (MINIMAL)
        data.append({
            "idx": "",
            "subject": p.subject,
            "indent": 0,
            "is_bold": 1
        })

        for i, task in enumerate(section["children"], start=1):
            data.append({
                "idx": i,
                "subject": task.subject,
                "start_date": task.exp_start_date,
                "end_date": task.exp_end_date,
                "progress": f"{task.progress or 0}%",
                "description": task.description,
                "indent": 1
            })

    return data