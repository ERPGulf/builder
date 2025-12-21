frappe.ui.form.on('ToDo', {
    onload: function(frm) {
        if (frm.fields_dict.allocated_to) {
            frm.fields_dict.allocated_to.get_query = function() {
                return {
                    query: "builder_erpgulf.todo_user_query.user_with_employee_id"
                };
            };
        }
    }
});
