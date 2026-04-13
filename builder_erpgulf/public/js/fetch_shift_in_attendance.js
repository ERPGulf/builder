frappe.ui.form.on("Attendance", {
	refresh(frm) {
		if (frm.doc.docstatus !== 0) return;

		if (frm.fetch_shift_added) return;
		frm.fetch_shift_added = true;

		frm.add_custom_button(__("Fetch Shift"), () => {
			frappe.call({
				method: "builder_erpgulf.hrms.attendance.fetch_shift_for_attendance",
				args: {
					attendance: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Fetching Shift"),
				callback(r) {
					if (r.message && r.message.shift) {
						frappe.show_alert(
							{
								message: __("Shift updated to {0}", [r.message.shift]),
								indicator: "green",
							},
							5
						);
						frm.reload_doc();
					} else {
						frappe.show_alert(
							{
								message: __("No valid shift found for attendance date"),
								indicator: "orange",
							},
							5
						);
					}
				},
			});
		});
	},
});