frappe.ui.form.on("Project", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(
                __("Site Activities"),
                function () {
                    frappe.set_route(
                        "query-report",
                        "Site Activities Report",
                        { project: frm.doc.name }
                    );
                },
                __("Actions")
            );
        }
    }
});