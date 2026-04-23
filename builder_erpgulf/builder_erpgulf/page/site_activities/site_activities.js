frappe.pages["site-activities"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Site Activities"),
        single_column: true
    });

    const project = frappe.get_route()[1];

    if (!project) {
        page.body.html(`<div class="alert alert-warning">Project not specified</div>`);
        return;
    }

    const wrapper_el = $('<div class="mt-4"></div>').appendTo(page.body);

    /**
     * @param {String} title
     * @param {Array} data
     * @param {Boolean} parent_minimal
     *        false → show full parent data (TABLE 1)
     *        true  → show only description for parent (TABLE 2)
     */
    function build_table(title, data, parent_minimal = false) {
        let body_html = "";

        data.forEach(section => {
            const p = section.parent;

            if (parent_minimal) {
                body_html += `
                    <tr class="table-active font-weight-bold">
                        <td></td>
                        <td>${p.subject || ""}</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                `;
            } else {
                body_html += `
                    <tr class="table-active font-weight-bold">
                        <td></td>
                        <td>${p.subject || ""}</td>
                        <td></td>
                        <td>${p.exp_start_date || ""}</td>
                        <td>${p.exp_end_date || ""}</td>
                        <td>${p.progress || 0}%</td>
                        <td>${p.description || ""}</td>
                    </tr>
                `;
            }

            section.children.forEach((task, idx) => {
                body_html += `
                    <tr>
                        <td>${idx + 1}</td>
                        <td>${task.subject || ""}</td>
                        <td></td>
                        <td>${task.exp_start_date || ""}</td>
                        <td>${task.exp_end_date || ""}</td>
                        <td>${task.progress || 0}%</td>
                        <td>${task.description || ""}</td>
                    </tr>
                `;
            });
        });

        return `
            <h4 class="mt-5 mb-3">${title}</h4>
            <table class="table table-bordered table-hover">
                <thead>
                    <tr>
                        <th>Act #</th>
                        <th>Act. Description</th>
                        <th>Area</th>
                        <th>Date Started</th>
                        <th>Date Completed</th>
                        <th>% Comp.</th>
                        <th>Remarks</th>
                    </tr>
                </thead>
                <tbody>
                    ${body_html || `
                        <tr>
                            <td colspan="7" class="text-muted text-center">
                                No activities found
                            </td>
                        </tr>
                    `}
                </tbody>
            </table>
        `;
    }

    function load_data() {
        frappe.call({
            method: "builder_erpgulf.builder_erpgulf.page.site_activities.site_activities.get_project_activities",
            args: { project },
            callback(r) {
                if (!r.message) return;

                wrapper_el.html(`
                    ${build_table(
                        "Activities in Progress",
                        r.message.in_progress,
                        false   
                    )}
                    ${build_table(
                        "Activities Planned for the Next Day",
                        r.message.next_day,
                        true    
                    )}
                `);
            }
        });
    }

    load_data();

    setInterval(load_data, 30000);
};