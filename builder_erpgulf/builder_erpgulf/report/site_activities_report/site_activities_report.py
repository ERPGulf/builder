
# import frappe
# from frappe.utils import getdate, today
# import datetime
# import re

# def strip_html(text):
#     if not text:
#         return ""
#     clean = re.sub(r'<[^>]+>', '', text)
#     clean = clean.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
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

#     filter_date = (filters or {}).get("date")

#     # ── Fetch Project for name/status/priority/percent_complete/company/customer ──
#     project = frappe.get_doc("Project", project_name)

#     # ── Fetch Project Progress for this project + date ──
#     pp_filters = {"project": project_name}
#     if filter_date:
#         pp_filters["date"] = getdate(filter_date)

#     pp_list = frappe.db.get_all(
#         "Project Progress",
#         filters=pp_filters,
#         fields=["name"],
#         order_by="modified desc",
#         limit=1
#     )
#     if not pp_list:
#         return rows

#     pp = frappe.get_doc("Project Progress", pp_list[0].name)

#     # ── Client logo from Customer ──
#     client_logo = ""
#     if project.get("customer"):
#         try:
#             customer = frappe.get_doc("Customer", project.customer)
#             client_logo = customer.get("client_logo") or ""
#         except Exception:
#             client_logo = ""

#     # ── Date / weather from Project Progress ──
#     report_date = getdate(pp.get("date") or today())
#     today_date  = getdate(today())

#     day_abbr       = report_date.strftime("%A")[:2].upper()
#     formatted_date = report_date.strftime("%d.%m.%Y")

#     custom_temp     = pp.get("temp")     or ""
#     custom_wind     = pp.get("wind")     or ""
#     custom_humidity = pp.get("humidity") or ""
#     custom_weather  = pp.get("weather")  or ""
#     custom_sea      = pp.get("sea")      or ""

#     # ── HEADER ──
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

#     # ── MACHINERY ──
#     rows.append({"section": "MACHINERY_HEADER"})
#     for idx, m in enumerate(pp.machinery_and_equipments_used or [], start=1):
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

#     # ── MATERIALS ──
#     rows.append({"section": "MATERIAL_HEADER"})
#     for m in pp.materials_delivered_to_site or []:
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

#     # ── MANPOWER ──
#     rows.append({"section": "MANPOWER_HEADER"})
#     for m in pp.manpower_available_at_site or []:
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

#     # ── ACTIVITIES IN PROGRESS ──
#     rows.append({"section": "INPROGRESS_HEADER"})
#     for idx, a in enumerate(pp.activities_in_progress or [], start=1):
#         rows.append({
#             "section":      "ACTIVITY_CHILD",
#             "act_no":       idx,
#             "description":  a.description,
#             "area":         a.area or "",
#             "date_started": str(a.start) if a.get("start") else "",
#             "date_ended":   str(a.end)   if a.get("end")   else "",
#             "pct":          str(int(a._progress or 0)) + "%" if a.get("_progress") is not None else "0%",
#             "remarks":      strip_html(a.remarks or ""),
#         })

#     # ── ACTIVITIES PLANNED FOR NEXT DAY ──
#     rows.append({"section": "NEXTDAY_HEADER"})
#     next_day_items = pp.activities_planned_for_the_next_day or []
#     if next_day_items:
#         for idx, a in enumerate(next_day_items, start=1):
#             rows.append({
#                 "section":      "NEXTDAY_CHILD",
#                 "act_no":       idx,
#                 "description":  a.description,
#                 "area":         a.area or "",
#                 "date_started": str(a.start) if a.get("start") else "",
#                 "date_ended":   str(a.end)   if a.get("end")   else "",
#                 "pct":          str(int(a._progress or 0)) + "%" if a.get("_progress") is not None else "0%",
#                 "remarks":      strip_html(a.remarks or ""),
#             })
#     else:
#         rows.append({"section": "NEXTDAY_EMPTY"})

#     # ── ISSUES ──
#     rows.append({"section": "ISSUES_HEADER"})
#     issues = pp.issues or []
#     for idx, i in enumerate(issues, start=1):
#         rows.append({
#             "section": "ISSUE",
#             "no":      idx,
#             "issues":  i.issues,
#         })
#     if not issues:
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

    filter_date = (filters or {}).get("date")

    # ── Fetch Project for name/status/priority/percent_complete/company/customer ──
    project = frappe.get_doc("Project", project_name)

    # ── Fetch Project Progress for this project + date ──
    pp_filters = {"project": project_name}
    if filter_date:
        pp_filters["date"] = getdate(filter_date)

    pp_list = frappe.db.get_all(
        "Project Progress",
        filters=pp_filters,
        fields=["name"],
        order_by="modified desc",
        limit=1
    )
    if not pp_list:
        return rows

    pp = frappe.get_doc("Project Progress", pp_list[0].name)

    # ── Client logo from Customer ──
    client_logo = ""
    if project.get("customer"):
        try:
            customer = frappe.get_doc("Customer", project.customer)
            client_logo = customer.get("client_logo") or ""
        except Exception:
            client_logo = ""

    # ── Date / weather from Project Progress ──
    report_date = getdate(pp.get("date") or today())
    today_date  = getdate(today())

    day_abbr       = report_date.strftime("%A")[:2].upper()
    formatted_date = report_date.strftime("%d.%m.%Y")

    custom_temp     = pp.get("temp")     or ""
    custom_wind     = pp.get("wind")     or ""
    custom_humidity = pp.get("humidity") or ""
    custom_weather  = pp.get("weather")  or ""
    custom_sea      = pp.get("sea")      or ""

    # ── HEADER ──
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

    # ── MACHINERY ──
    rows.append({"section": "MACHINERY_HEADER"})
    for idx, m in enumerate(pp.machinery_and_equipments_used or [], start=1):
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

    # ── MATERIALS ──
    rows.append({"section": "MATERIAL_HEADER"})
    for m in pp.materials_delivered_to_site or []:
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

    # ── MANPOWER ──
    rows.append({"section": "MANPOWER_HEADER"})
    for m in pp.manpower_available_at_site or []:
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

    # ── SUBCONTRACTOR MANPOWER ──
    rows.append({"section": "SUBCON_MANPOWER_HEADER"})
    for m in pp.subcontractor_manpower or []:
        rows.append({
            "section":           "SUBCON_MANPOWER",
            "labor_occupation":  m.labor_occupation,
            "staff":             m.staff,
            "staff_occupation":  m.staff_occupation,
            "skilled":           m.skilled,
            "unskilled":         m.unskilled,
            "daily_total_units": m.daily_total_units,
            "hours":             m.hours,
        })

    # ── ACTIVITIES IN PROGRESS ──
    rows.append({"section": "INPROGRESS_HEADER"})
    for idx, a in enumerate(pp.activities_in_progress or [], start=1):
        rows.append({
            "section":      "ACTIVITY_CHILD",
            "act_no":       idx,
            "description":  a.description,
            "area":         a.area or "",
            "date_started": str(a.start) if a.get("start") else "",
            "date_ended":   str(a.end)   if a.get("end")   else "",
            "pct":          str(int(a._progress or 0)) + "%" if a.get("_progress") is not None else "0%",
            "remarks":      strip_html(a.remarks or ""),
        })

    # ── ACTIVITIES PLANNED FOR NEXT DAY ──
    rows.append({"section": "NEXTDAY_HEADER"})
    next_day_items = pp.activities_planned_for_the_next_day or []
    if next_day_items:
        for idx, a in enumerate(next_day_items, start=1):
            rows.append({
                "section":      "NEXTDAY_CHILD",
                "act_no":       idx,
                "description":  a.description,
                "area":         a.area or "",
                "date_started": str(a.start) if a.get("start") else "",
                "date_ended":   str(a.end)   if a.get("end")   else "",
                "pct":          str(int(a._progress or 0)) + "%" if a.get("_progress") is not None else "0%",
                "remarks":      strip_html(a.remarks or ""),
            })
    else:
        rows.append({"section": "NEXTDAY_EMPTY"})

    # ── ISSUES ──
    rows.append({"section": "ISSUES_HEADER"})
    issues = pp.issues or []
    for idx, i in enumerate(issues, start=1):
        rows.append({
            "section": "ISSUE",
            "no":      idx,
            "issues":  i.issues,
        })
    if not issues:
        rows.append({"section": "ISSUES_EMPTY"})

    return rows