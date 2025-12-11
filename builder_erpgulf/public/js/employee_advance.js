frappe.ui.form.on('Employee Advance', {
    employee: function(frm) {
        if (!frm.doc.employee) return;

        frappe.call({
            method: "builder_erpgulf.salary.get_allowed_advance",
            args: {
                employee: frm.doc.employee
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("allowed_advance", r.message);
                } else {
                    frm.set_value("allowed_advance", 0);
                }
            }
        });
    }
});
