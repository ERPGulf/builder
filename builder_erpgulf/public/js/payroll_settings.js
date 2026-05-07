frappe.ui.form.on("Payroll Settings", {
    refresh(frm) {
        frm.set_query("salary_deduction_component", function() {
            return {
                filters: {
                    type: "Deduction"
                }
            };
        });
    }
});