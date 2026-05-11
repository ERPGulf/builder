
# import frappe
# from frappe.utils import getdate, today
# import datetime
# import re

# def strip_html(text):
#     if not text:
#         return ""
#     # Remove all HTML tags
#     clean = re.sub(r'<[^>]+>', '', text)
#     # Decode HTML entities
#     clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
#     # Collapse whitespace/newlines
#     clean = ' '.join(clean.split())
#     return clean.strip()

# def execute(filters=None):
#     columns = [{"fieldname": "section", "label": "Section", "fieldtype": "Data", "width": 120}]
#     data = get_report_data(filters)
#     return columns, data


# def get_report_data(filters):
#     rows = []
#     project_name = (filters or {}).get("project")
#     if not project_name:
#         return rows

#     project = frappe.get_doc("Project", project_name)
#     today_date = getdate(today())

#     client_logo = ""
#     if project.get("customer"):
#         try:
#             customer = frappe.get_doc("Customer", project.customer)
#             client_logo = customer.get("client_logo") or ""
#         except Exception:
#             client_logo = ""

#     day_abbr = today_date.strftime("%A")[:2].upper()
#     formatted_date = today_date.strftime("%d.%m.%Y")

#     custom_temp      = project.get("custom_temp")      or ""
#     custom_wind      = project.get("custom_wind")      or ""
#     custom_humidity  = project.get("custom_humidity")  or ""
#     custom_weather   = project.get("custom_weather")   or ""
#     custom_sea       = project.get("custom_sea")       or ""

#     rows.append({
#         "section":          "HEADER",
#         "project_ref":      project.name,
#         "project_name":     project.project_name,
#         "company":          project.company,
#         "status":           project.status,
#         "priority":         project.priority,
#         "percent_complete": project.percent_complete or 0,
#         "client_logo":      client_logo,
#         "day_abbr":         day_abbr,
#         "formatted_date":   formatted_date,
#         "custom_temp":      custom_temp,
#         "custom_wind":      custom_wind,
#         "custom_humidity":  custom_humidity,
#         "custom_weather":   custom_weather,
#         "custom_sea":       custom_sea,
#     })

#     rows.append({"section": "MACHINERY_HEADER"})
#     for idx, m in enumerate(project.machinery_and_equipments_used or [], start=1):
#         rows.append({
#             "section":     "MACHINERY",
#             "no":          idx,
#             "description": m.description,
#             "size":        m.size,
#             "area":        m.area,
#             "no_on_site":  m.no_on_site,
#             "down_time":   m.down_time,
#             "total_hours": m.total_working_hours,
#             "remarks":     m.remarks,
#         })

#     rows.append({"section": "MATERIAL_HEADER"})
#     for m in project.materials_delivered_to_site or []:
#         rows.append({
#             "section":     "MATERIAL",
#             "time":        m.time,
#             "description": m.description,
#             "ticket_no":   m.ticket_no,
#             "boq_no":      m.boq_no_pageitem_no,
#             "quantity":    m.quantity,
#             "units":       m.units,
#             "area":        m.area,
#             "origin":      m.origin__manufacturer,
#             "remarks":     m.remarks,
#         })

#     rows.append({"section": "MANPOWER_HEADER"})
#     for m in project.manpower_available_at_site or []:
#         rows.append({
#             "section":           "MANPOWER",
#             "labor_occupation":  m.labor_occupation,
#             "staff":             m.staff,
#             "staff_occupation":  m.staff_occupation,
#             "skilled":           m.skilled,
#             "unskilled":         m.unskilled,
#             "daily_total_units": m.daily_total_units,
#             "hours":             m.hours,
#         })

#     parents = frappe.db.get_all(
#         "Task",
#         filters={"project": project_name, "is_group": 1},
#         fields=["name", "subject", "exp_start_date", "exp_end_date",
#                 "progress", "custom_location", "description"],
#         order_by="creation asc"
#     )

#     rows.append({"section": "INPROGRESS_HEADER"})
#     act_no = 0
#     for parent in parents:
#         rows.append({
#             "section":      "ACTIVITY_PARENT",
#             "act_no":       "",
#             "description":  parent.subject,
#             "area":         parent.custom_location or "",
#             "date_started": str(parent.exp_start_date) if parent.exp_start_date else "",
#             "date_ended":   str(parent.exp_end_date)   if parent.exp_end_date   else "",
#             "pct":          str(int(parent.progress or 0)) + "%",
#             "remarks":      strip_html(parent.description or ""),
#         })

#         children = frappe.db.get_all(
#             "Task",
#             filters={"project": project_name, "parent_task": parent.name},
#             fields=["name", "subject", "exp_start_date", "exp_end_date",
#                     "progress", "custom_location", "description"],
#             order_by="creation asc"
#         )
#         for idx, child in enumerate(children, start=1):
#             act_no += 1
#             rows.append({
#                 "section":      "ACTIVITY_CHILD",
#                 "act_no":       idx,
#                 "description":  child.subject,
#                 "area":         child.custom_location or "",
#                 "date_started": str(child.exp_start_date) if child.exp_start_date else "",
#                 "date_ended":   str(child.exp_end_date)   if child.exp_end_date   else "",
#                 "pct":          str(int(child.progress or 0)) + "%",
#                 "remarks":      strip_html(child.description or ""),
#             })

#     rows.append({"section": "NEXTDAY_HEADER"})
#     has_next = False
#     for parent in parents:
#         children = frappe.db.get_all(
#             "Task",
#             filters={"project": project_name, "parent_task": parent.name},
#             fields=["name", "subject", "exp_start_date", "exp_end_date",
#                     "progress", "custom_location", "description"],
#             order_by="creation asc"
#         )
#         future = [c for c in children
#                   if c.exp_start_date and getdate(c.exp_start_date) > today_date]

#         if future:
#             rows.append({
#                 "section":      "ACTIVITY_PARENT",
#                 "act_no":       "",
#                 "description":  parent.subject,
#                 "area":         parent.custom_location or "",
#                 "date_started": str(parent.exp_start_date) if parent.exp_start_date else "",
#                 "date_ended":   str(parent.exp_end_date)   if parent.exp_end_date   else "",
#                 "pct":          str(int(parent.progress or 0)) + "%",
#                 "remarks":      strip_html(parent.description or ""),
#             })
#             for idx, child in enumerate(future, start=1):
#                 rows.append({
#                     "section":      "NEXTDAY_CHILD",
#                     "act_no":       idx,
#                     "description":  child.subject,
#                     "area":         child.custom_location or "",
#                     "date_started": str(child.exp_start_date) if child.exp_start_date else "",
#                     "date_ended":   str(child.exp_end_date)   if child.exp_end_date   else "",
#                     "pct":          str(int(child.progress or 0)) + "%",
#                     "remarks":      strip_html(child.description or ""),
#                 })
#             has_next = True

#     if not has_next:
#         rows.append({"section": "NEXTDAY_EMPTY"})

#     rows.append({"section": "ISSUES_HEADER"})
#     for idx, i in enumerate(project.custom_issues or [], start=1):
#         rows.append({
#             "section": "ISSUE",
#             "no":      idx,
#             "issues":  i.issues,
#         })
#     if not project.custom_issues:
#         rows.append({"section": "ISSUES_EMPTY"})

#     return rows
import frappe
from frappe.utils import getdate, today
import datetime
import re

def strip_html(text):
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    clean = ' '.join(clean.split())
    return clean.strip()

def execute(filters=None):
    columns = [{"fieldname": "section", "label": "Section", "fieldtype": "Data", "width": 120}]
    data = get_report_data(filters)
    return columns, data


def get_report_data(filters):
    rows = []
    project_name = (filters or {}).get("project")
    if not project_name:
        return rows

    project = frappe.get_doc("Project", project_name)
    today_date = getdate(today())

    client_logo = ""
    if project.get("customer"):
        try:
            customer = frappe.get_doc("Customer", project.customer)
            client_logo = customer.get("client_logo") or ""
        except Exception:
            client_logo = ""

    day_abbr = today_date.strftime("%A")[:2].upper()
    formatted_date = today_date.strftime("%d.%m.%Y")

    custom_temp      = project.get("custom_temp")      or ""
    custom_wind      = project.get("custom_wind")      or ""
    custom_humidity  = project.get("custom_humidity")  or ""
    custom_weather   = project.get("custom_weather")   or ""
    custom_sea       = project.get("custom_sea")       or ""

    rows.append({
        "section":          "HEADER",
        "project_ref":      project.name,
        "project_name":     project.project_name,
        "company":          project.company,
        "status":           project.status,
        "priority":         project.priority,
        "percent_complete": project.percent_complete or 0,
        "client_logo":      client_logo,
        "day_abbr":         day_abbr,
        "formatted_date":   formatted_date,
        "custom_temp":      custom_temp,
        "custom_wind":      custom_wind,
        "custom_humidity":  custom_humidity,
        "custom_weather":   custom_weather,
        "custom_sea":       custom_sea,
    })

    rows.append({"section": "MACHINERY_HEADER"})
    for idx, m in enumerate(project.machinery_and_equipments_used or [], start=1):
        rows.append({
            "section":     "MACHINERY",
            "no":          idx,
            "description": m.description,
            "size":        m.size,
            "area":        m.area,
            "no_on_site":  m.no_on_site,
            "down_time":   m.down_time,
            "total_hours": m.total_working_hours,
            "remarks":     m.remarks,
        })

    rows.append({"section": "MATERIAL_HEADER"})
    for m in project.materials_delivered_to_site or []:
        rows.append({
            "section":     "MATERIAL",
            "time":        m.time,
            "description": m.description,
            "ticket_no":   m.ticket_no,
            "boq_no":      m.boq_no_pageitem_no,
            "quantity":    m.quantity,
            "units":       m.units,
            "area":        m.area,
            "origin":      m.origin__manufacturer,
            "remarks":     m.remarks,
        })

    rows.append({"section": "MANPOWER_HEADER"})
    for m in project.manpower_available_at_site or []:
        rows.append({
            "section":           "MANPOWER",
            "labor_occupation":  m.labor_occupation,
            "staff":             m.staff,
            "staff_occupation":  m.staff_occupation,
            "skilled":           m.skilled,
            "unskilled":         m.unskilled,
            "daily_total_units": m.daily_total_units,
            "hours":             m.hours,
        })

    # Fetch ALL parent tasks (used for Next Day section)
    parents = frappe.db.get_all(
        "Task",
        filters={"project": project_name, "is_group": 1},
        fields=["name", "subject", "exp_start_date", "exp_end_date",
                "progress", "custom_location", "description"],
        order_by="creation asc"
    )

    # ── ACTIVITIES IN PROGRESS ──
    # Show ONLY child tasks with status = "Working" — no parent rows
    rows.append({"section": "INPROGRESS_HEADER"})
    act_no = 0
    for parent in parents:
        working_children = frappe.db.get_all(
            "Task",
            filters={"project": project_name, "parent_task": parent.name, "status": "Working"},
            fields=["name", "subject", "exp_start_date", "exp_end_date",
                    "progress", "custom_location", "description"],
            order_by="creation asc"
        )
        for child in working_children:
            act_no += 1
            rows.append({
                "section":      "ACTIVITY_CHILD",
                "act_no":       act_no,
                "description":  child.subject,
                "area":         child.custom_location or "",
                "date_started": str(child.exp_start_date) if child.exp_start_date else "",
                "date_ended":   str(child.exp_end_date)   if child.exp_end_date   else "",
                "pct":          str(int(child.progress or 0)) + "%",
                "remarks":      strip_html(child.description or ""),
            })

    # ── NEXT DAY (unchanged — all parents/children, future start date) ──
    rows.append({"section": "NEXTDAY_HEADER"})
    has_next = False
    for parent in parents:
        children = frappe.db.get_all(
            "Task",
            filters={"project": project_name, "parent_task": parent.name},
            fields=["name", "subject", "exp_start_date", "exp_end_date",
                    "progress", "custom_location", "description"],
            order_by="creation asc"
        )
        future = [c for c in children
                  if c.exp_start_date and getdate(c.exp_start_date) > today_date]

        if future:
            rows.append({
                "section":      "ACTIVITY_PARENT",
                "act_no":       "",
                "description":  parent.subject,
                "area":         parent.custom_location or "",
                "date_started": str(parent.exp_start_date) if parent.exp_start_date else "",
                "date_ended":   str(parent.exp_end_date)   if parent.exp_end_date   else "",
                "pct":          str(int(parent.progress or 0)) + "%",
                "remarks":      strip_html(parent.description or ""),
            })
            for idx, child in enumerate(future, start=1):
                rows.append({
                    "section":      "NEXTDAY_CHILD",
                    "act_no":       idx,
                    "description":  child.subject,
                    "area":         child.custom_location or "",
                    "date_started": str(child.exp_start_date) if child.exp_start_date else "",
                    "date_ended":   str(child.exp_end_date)   if child.exp_end_date   else "",
                    "pct":          str(int(child.progress or 0)) + "%",
                    "remarks":      strip_html(child.description or ""),
                })
            has_next = True

    if not has_next:
        rows.append({"section": "NEXTDAY_EMPTY"})

    rows.append({"section": "ISSUES_HEADER"})
    for idx, i in enumerate(project.custom_issues or [], start=1):
        rows.append({
            "section": "ISSUE",
            "no":      idx,
            "issues":  i.issues,
        })
    if not project.custom_issues:
        rows.append({"section": "ISSUES_EMPTY"})

    return rows