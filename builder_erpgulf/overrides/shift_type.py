# from datetime import datetime
# import frappe
# from frappe.utils import getdate, get_datetime
# from hrms.hr.doctype.shift_type.shift_type import ShiftType
# from hrms.hr.doctype.shift_assignment.shift_assignment import (
#     get_employee_shift,
#     get_shift_details
# )

# class SameDayAbsentShiftType(ShiftType):

#     def get_start_and_end_dates(self, employee):
#         """
#         SAME-DAY absent override
#         Removes the 1-day buffer used by ERPNext
#         """

#         date_of_joining, relieving_date, employee_creation = frappe.get_cached_value(
#             "Employee",
#             employee,
#             ["date_of_joining", "relieving_date", "creation"],
#         )

#         if not date_of_joining:
#             date_of_joining = employee_creation.date()

#         start_date = max(getdate(self.process_attendance_after), date_of_joining)
#         end_date = None

#         shift_details = get_shift_details(
#             self.name,
#             get_datetime(self.last_sync_of_checkin),
#         )

#         last_shift_time = (
#             shift_details.actual_end
#             if shift_details
#             else get_datetime(self.last_sync_of_checkin)
#         )

#         prev_shift = get_employee_shift(
#             employee,
#             last_shift_time,
#             True,
#             "reverse",
#         )

#         if prev_shift and prev_shift.shift_type.name == self.name:
#             end_date = (
#                 min(prev_shift.start_datetime.date(), relieving_date)
#                 if relieving_date
#                 else prev_shift.start_datetime.date()
#             )
#         else:
#             return None, None

#         return start_date, end_date



import frappe

from datetime import datetime
from itertools import groupby

from frappe.utils import getdate, get_datetime, get_time, flt

from hrms.hr.doctype.shift_type.shift_type import (
    ShiftType,
    EMPLOYEE_CHUNK_SIZE,
    create_batch,
)

from hrms.hr.doctype.shift_assignment.shift_assignment import (
    get_employee_shift,
    get_shift_details,
)

from hrms.hr.doctype.employee_checkin.employee_checkin import (
    mark_attendance_and_link_log,
)

from hrms.hr.doctype.attendance.attendance import mark_attendance


class SameDayAbsentShiftType(ShiftType):

    # ---------------------------------------------------------
    # Draft Attendance Request Check
    # ---------------------------------------------------------

    def has_pending_attendance_request(self, employee, attendance_date):
        """
        Check if the employee has an Attendance Request covering the date
        which is still pending, including workflow pending states.
        """

        requests = frappe.get_all(
            "Attendance Request",
            filters={
                "employee": employee,
                "from_date": ["<=", attendance_date],
                "to_date": [">=", attendance_date],
                "docstatus": ["<", 2],
            },
            fields=[
                "name",
                "docstatus",
                "workflow_state",
            ],
        )

        for request in requests:

            # Submitted request → allow normal Attendance Request processing
            if request.docstatus == 1:
                continue

            # Draft / Workflow Pending → block auto attendance
            if request.docstatus == 0:
                return True

        return False

    # ---------------------------------------------------------
    # SAME-DAY ABSENT OVERRIDE
    # ---------------------------------------------------------

    def get_start_and_end_dates(self, employee):
        """
        SAME-DAY absent override.

        Removes the 1-day buffer used by ERPNext/HRMS.
        """

        date_of_joining, relieving_date, employee_creation = frappe.get_cached_value(
            "Employee",
            employee,
            ["date_of_joining", "relieving_date", "creation"],
        )

        if not date_of_joining:
            date_of_joining = employee_creation.date()

        start_date = max(
            getdate(self.process_attendance_after),
            date_of_joining,
        )

        end_date = None

        shift_details = get_shift_details(
            self.name,
            get_datetime(self.last_sync_of_checkin),
        )

        last_shift_time = (
            shift_details.actual_end
            if shift_details
            else get_datetime(self.last_sync_of_checkin)
        )

        prev_shift = get_employee_shift(
            employee,
            last_shift_time,
            True,
            "reverse",
        )

        if prev_shift and prev_shift.shift_type.name == self.name:
            end_date = (
                min(
                    prev_shift.start_datetime.date(),
                    relieving_date,
                )
                if relieving_date
                else prev_shift.start_datetime.date()
            )
        else:
            return None, None

        return start_date, end_date

    # ---------------------------------------------------------
    # AUTO ATTENDANCE PROCESSING
    # ---------------------------------------------------------

    def _process(self, logs):
        """
        Process attendance from Employee Checkins.

        Custom behavior:
        If an employee has a Draft Attendance Request for the
        attendance date, attendance processing is skipped.
        """

        group_key = lambda x: (x["employee"], x["shift_start"])

        for key, group in groupby(
            sorted(logs, key=group_key),
            key=group_key,
        ):
            single_shift_logs = list(group)

            attendance_date = key[1].date()
            employee = key[0]

            # -------------------------------------------------
            # CUSTOM CHECK
            # -------------------------------------------------
            # Do not process attendance while an Attendance
            # Request for this employee/date is still Draft.
            # -------------------------------------------------

            if self.has_pending_attendance_request(
                employee,
                attendance_date,
            ):
                continue

            # -------------------------------------------------
            # Existing HRMS logic
            # -------------------------------------------------

            if not self.should_mark_attendance(
                employee,
                attendance_date,
            ):
                continue

            working_hours_threshold_for_half_day = flt(
                self.working_hours_threshold_for_half_day
            )

            working_hours_threshold_for_absent = flt(
                self.working_hours_threshold_for_absent
            )

            if self.is_half_holiday(
                employee,
                attendance_date,
            ):
                working_hours_threshold_for_half_day = (
                    flt(
                        self.working_hours_threshold_for_half_day
                    )
                    / 2
                )

                working_hours_threshold_for_absent = (
                    flt(
                        self.working_hours_threshold_for_absent
                    )
                    / 2
                )

            overtime_type = single_shift_logs[0].get(
                "overtime_type"
            )

            (
                attendance_status,
                working_hours,
                late_entry,
                early_exit,
                in_time,
                out_time,
            ) = self.get_attendance(
                single_shift_logs,
                working_hours_threshold_for_absent,
                working_hours_threshold_for_half_day,
            )

            mark_attendance_and_link_log(
                single_shift_logs,
                attendance_status,
                attendance_date,
                working_hours,
                late_entry,
                early_exit,
                in_time,
                out_time,
                self.name,
                overtime_type,
            )

        # -----------------------------------------------------
        # Commit after processing check-in logs
        # -----------------------------------------------------

        if not frappe.in_test:
            frappe.db.commit()

        # -----------------------------------------------------
        # Mark absent
        # -----------------------------------------------------

        assigned_employees = self.get_assigned_employees(
            self.process_attendance_after,
            True,
        )

        for batch in create_batch(
            assigned_employees,
            EMPLOYEE_CHUNK_SIZE,
        ):
            for employee in batch:

                self.mark_absent_for_dates_with_no_attendance(
                    employee
                )

                self.mark_absent_for_half_day_dates(
                    employee
                )

            if not frappe.in_test:
                frappe.db.commit()

    # ---------------------------------------------------------
    # ABSENT ATTENDANCE
    # ---------------------------------------------------------

    def mark_absent_for_dates_with_no_attendance(
        self,
        employee: str,
    ):
        """
        Same as the standard HRMS method, except that dates
        having a Draft Attendance Request are skipped.
        """

        start_time = get_time(self.start_time)

        dates = self.get_dates_for_attendance(employee)

        for date in dates:

            # -------------------------------------------------
            # CUSTOM CHECK
            # -------------------------------------------------
            # Do not mark Absent while Attendance Request is
            # still Draft.
            # -------------------------------------------------

            if self.has_pending_attendance_request(
                employee,
                date,
            ):
                continue

            timestamp = datetime.combine(
                date,
                start_time,
            )

            shift_details = get_employee_shift(
                employee,
                timestamp,
                True,
            )

            if (
                shift_details
                and shift_details.shift_type.name == self.name
            ):
                attendance = mark_attendance(
                    employee,
                    date,
                    "Absent",
                    self.name,
                )

                if not attendance:
                    continue

                frappe.get_doc(
                    {
                        "doctype": "Comment",
                        "comment_type": "Comment",
                        "reference_doctype": "Attendance",
                        "reference_name": attendance,
                        "content": frappe._(
                            "Employee was marked Absent due to missing Employee Checkins."
                        ),
                    }
                ).insert(ignore_permissions=True)