import frappe
from frappe.utils import getdate, today

@frappe.whitelist()
def get_project_activities(project=None):
    if not project:
        return {}

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

    activities_in_progress = []
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

        activities_in_progress.append({
            "parent": parent,
            "children": children
        })

        future_children = [
            c for c in children
            if c.exp_start_date and getdate(c.exp_start_date) > today_date
        ]

        if future_children:
            activities_next_day.append({
                "parent": parent,
                "children": future_children
            })

    return {
        "in_progress": activities_in_progress,
        "next_day": activities_next_day
    }