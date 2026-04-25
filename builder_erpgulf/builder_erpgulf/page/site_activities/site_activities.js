// // frappe.pages["site-activities"].on_page_load = function (wrapper) {
// //     const page = frappe.ui.make_app_page({
// //         parent: wrapper,
// //         title: __("Site Activities"),
// //         single_column: true
// //     });

// //     const project = frappe.get_route()[1];

// //     if (!project) {
// //         page.body.html(`<div class="alert alert-warning">Project not specified</div>`);
// //         return;
// //     }

// //     const wrapper_el = $('<div class="mt-4"></div>').appendTo(page.body);

// //     /**
// //      * @param {String} title
// //      * @param {Array} data
// //      * @param {Boolean} parent_minimal
// //      *        false → show full parent data (TABLE 1)
// //      *        true  → show only description for parent (TABLE 2)
// //      */
// //     function build_table(title, data, parent_minimal = false) {
// //         let body_html = "";

// //         data.forEach(section => {
// //             const p = section.parent;

// //             if (parent_minimal) {
// //                 body_html += `
// //                     <tr class="table-active font-weight-bold">
// //                         <td></td>
// //                         <td>${p.subject || ""}</td>
// //                         <td></td>
// //                         <td></td>
// //                         <td></td>
// //                         <td></td>
// //                         <td></td>
// //                     </tr>
// //                 `;
// //             } else {
// //                 body_html += `
// //                     <tr class="table-active font-weight-bold">
// //                         <td></td>
// //                         <td>${p.subject || ""}</td>
// //                         <td></td>
// //                         <td>${p.exp_start_date || ""}</td>
// //                         <td>${p.exp_end_date || ""}</td>
// //                         <td>${p.progress || 0}%</td>
// //                         <td>${p.description || ""}</td>
// //                     </tr>
// //                 `;
// //             }

// //             section.children.forEach((task, idx) => {
// //                 body_html += `
// //                     <tr>
// //                         <td>${idx + 1}</td>
// //                         <td>${task.subject || ""}</td>
// //                         <td></td>
// //                         <td>${task.exp_start_date || ""}</td>
// //                         <td>${task.exp_end_date || ""}</td>
// //                         <td>${task.progress || 0}%</td>
// //                         <td>${task.description || ""}</td>
// //                     </tr>
// //                 `;
// //             });
// //         });

// //         return `
// //             <h4 class="mt-5 mb-3">${title}</h4>
// //             <table class="table table-bordered table-hover">
// //                 <thead>
// //                     <tr>
// //                         <th>Act #</th>
// //                         <th>Act. Description</th>
// //                         <th>Area</th>
// //                         <th>Date Started</th>
// //                         <th>Date Completed</th>
// //                         <th>% Comp.</th>
// //                         <th>Remarks</th>
// //                     </tr>
// //                 </thead>
// //                 <tbody>
// //                     ${body_html || `
// //                         <tr>
// //                             <td colspan="7" class="text-muted text-center">
// //                                 No activities found
// //                             </td>
// //                         </tr>
// //                     `}
// //                 </tbody>
// //             </table>
// //         `;
// //     }

// //     function load_data() {
// //         frappe.call({
// //             method: "builder_erpgulf.builder_erpgulf.page.site_activities.site_activities.get_project_activities",
// //             args: { project },
// //             callback(r) {
// //                 if (!r.message) return;

// //                 wrapper_el.html(`
// //                     ${build_table(
// //                         "Activities in Progress",
// //                         r.message.in_progress,
// //                         false   
// //                     )}
// //                     ${build_table(
// //                         "Activities Planned for the Next Day",
// //                         r.message.next_day,
// //                         true    
// //                     )}
// //                 `);
// //             }
// //         });
// //     }

// //     load_data();

// //     setInterval(load_data, 30000);
// // };
// frappe.pages["site-activities"].on_page_load = function (wrapper) {

// 	const page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: __("Site Activities"),
// 		single_column: true
// 	});

// 	// PRINT BUTTON
// 	page.add_inner_button(__('Print'), () => {
// 		window.print();
// 	});

// 	// PRINT CSS
// 	if (!document.getElementById("site-activities-print-style")) {
// 		$(`<style id="site-activities-print-style">
// 		@media print {

// 			body * { visibility: hidden; }

// 			.page-content, .page-content * {
// 				visibility: visible;
// 			}

// 			.page-content {
// 				position: absolute;
// 				left: 0;
// 				top: 0;
// 				width: 100%;
// 			}

// 			/* PRINT HEADER */
// 			.print-heading {
// 				display: block !important;
// 				text-align: center;
// 				font-size: 22px;
// 				font-weight: bold;
// 				margin-bottom: 20px;
// 			}

// 			table {
// 				border-collapse: collapse;
// 			}

// 			th, td {
// 				border: 1px solid #000 !important;
// 			}
// 		}

// 		/* hide in screen */
// 		.print-heading {
// 			display: none;
// 		}
// 		</style>`).appendTo("head");
// 	}

// 	const project = frappe.get_route()[1];

// 	if (!project) {
// 		page.body.html(`<div class="alert alert-warning">Project not specified</div>`);
// 		return;
// 	}

// 	const wrapper_el = $('<div class="mt-4"></div>').appendTo(page.body);

// 	// ------------------------------------------
// 	// MACHINERY
// 	// ------------------------------------------
// 	function build_machinery_table(data) {
// 		let rows = "";

// 		(data || []).forEach((d, i) => {
// 			rows += `
// 				<tr>
// 					<td>${i + 1}</td>
// 					<td>${d.area || ""}</td>
// 					<td>${d.description || ""}</td>
// 					<td>${d.no_on_site || ""}</td>
// 					<td>${d.size || ""}</td>
// 					<td>${d.total_working_hours || 0}</td>
// 					<td>${d.down_time ? (d.down_time / 3600).toFixed(2) + " hrs" : ""}</td>
// 					<td>${d.remarks || ""}</td>
// 				</tr>
// 			`;
// 		});

// 		return `
// 			<h4>Machinery & Equipments Used</h4>
// 			<table class="table table-bordered">
// 				<thead>
// 					<tr>
// 						<th>#</th><th>Area</th><th>Description</th><th>No</th>
// 						<th>Size</th><th>Hours</th><th>Down Time</th><th>Remarks</th>
// 					</tr>
// 				</thead>
// 				<tbody>${rows || `<tr><td colspan="8">No data</td></tr>`}</tbody>
// 			</table>
// 		`;
// 	}

// 	// ------------------------------------------
// 	// MATERIALS
// 	// ------------------------------------------
// 	function build_materials_table(data) {
// 		let rows = "";

// 		(data || []).forEach((d, i) => {
// 			rows += `
// 				<tr>
// 					<td>${i + 1}</td>
// 					<td>${d.area || ""}</td>
// 					<td>${d.boq_no_pageitem_no || ""}</td>
// 					<td>${d.description || ""}</td>
// 					<td>${d.origin__manufacturer || ""}</td>
// 					<td>${d.quantity || ""}</td>
// 					<td>${d.units || ""}</td>
// 					<td>${d.ticket_no || ""}</td>
// 					<td>${d.time || ""}</td>
// 					<td>${d.remarks || ""}</td>
// 				</tr>
// 			`;
// 		});

// 		return `
// 			<h4>Materials Delivered to Site</h4>
// 			<table class="table table-bordered">
// 				<thead>
// 					<tr>
// 						<th>#</th><th>Area</th><th>BOQ</th><th>Description</th>
// 						<th>Manufacturer</th><th>Qty</th><th>Units</th>
// 						<th>Ticket</th><th>Time</th><th>Remarks</th>
// 					</tr>
// 				</thead>
// 				<tbody>${rows || `<tr><td colspan="10">No data</td></tr>`}</tbody>
// 			</table>
// 		`;
// 	}

// 	// ------------------------------------------
// 	// MANPOWER
// 	// ------------------------------------------
// 	function build_manpower_table(data) {
// 		let rows = "";

// 		(data || []).forEach((d, i) => {
// 			rows += `
// 				<tr>
// 					<td>${i + 1}</td>
// 					<td>${d.employee_id || ""}</td>
// 					<td>${d.name1 || ""}</td>
// 					<td>${d.labor_occupation || ""}</td>
// 					<td>${d.staff_occupation || ""}</td>
// 					<td>${d.hours || ""}</td>
// 					<td>${d.staff || ""}</td>
// 					<td>${d.skilled || ""}</td>
// 					<td>${d.unskilled || ""}</td>
// 					<td>${d.daily_total_units || ""}</td>
// 				</tr>
// 			`;
// 		});

// 		return `
// 			<h4>Manpower Available at Site</h4>
// 			<table class="table table-bordered">
// 				<thead>
// 					<tr>
// 						<th>#</th>
// 						<th>Employee ID</th>
// 						<th>Name</th>
// 						<th>Labor Occupation</th>
// 						<th>Staff Occupation</th>
// 						<th>Hours</th>
// 						<th>Staff</th>
// 						<th>Skilled</th>
// 						<th>Unskilled</th>
// 						<th>Total Units</th>
// 					</tr>
// 				</thead>
// 				<tbody>${rows || `<tr><td colspan="10">No data</td></tr>`}</tbody>
// 			</table>
// 		`;
// 	}

// 	// ------------------------------------------
// 	// ACTIVITIES (AREA FIXED)
// 	// ------------------------------------------
// 	function build_table(title, data, parent_minimal = false) {
// 		let body_html = "";

// 		(data || []).forEach(section => {
// 			const p = section.parent;

// 			body_html += `
// 				<tr class="table-active">
// 					<td></td>
// 					<td>${p.subject || ""}</td>
// 					<td>${p.custom_location || ""}</td>
// 					<td>${parent_minimal ? "" : (p.exp_start_date || "")}</td>
// 					<td>${parent_minimal ? "" : (p.exp_end_date || "")}</td>
// 					<td>${parent_minimal ? "" : (p.progress || 0) + "%"}</td>
// 					<td>${parent_minimal ? "" : (p.description || "")}</td>
// 				</tr>
// 			`;

// 			(section.children || []).forEach((t, i) => {
// 				body_html += `
// 					<tr>
// 						<td>${i + 1}</td>
// 						<td>${t.subject || ""}</td>
// 						<td>${t.custom_location || ""}</td>
// 						<td>${t.exp_start_date || ""}</td>
// 						<td>${t.exp_end_date || ""}</td>
// 						<td>${t.progress || 0}%</td>
// 						<td>${t.description || ""}</td>
// 					</tr>
// 				`;
// 			});
// 		});

// 		return `
// 			<h4>${title}</h4>
// 			<table class="table table-bordered">
// 				<thead>
// 					<tr>
// 						<th>#</th><th>Description</th><th>Area</th>
// 						<th>Start</th><th>End</th><th>%</th><th>Remarks</th>
// 					</tr>
// 				</thead>
// 				<tbody>${body_html || `<tr><td colspan="7">No data</td></tr>`}</tbody>
// 			</table>
// 		`;
// 	}

// 	// ------------------------------------------
// 	// LOAD DATA
// 	// ------------------------------------------
// 	function load_data() {
// 		frappe.call({
// 			method: "builder_erpgulf.builder_erpgulf.page.site_activities.site_activities.get_project_activities",
// 			args: { project },
// 			callback(r) {
// 				if (!r.message) return;

// 				wrapper_el.html(`
// 					<div class="print-heading">
// 						Site Activities - ${r.message.project_name || project}
// 					</div>

// 					${build_machinery_table(r.message.machinery)}
// 					${build_materials_table(r.message.materials)}
// 					${build_manpower_table(r.message.manpower)}

// 					${build_table("Activities in Progress", r.message.in_progress)}
// 					${build_table("Activities Planned for the Next Day", r.message.next_day, true)}
// 				`);
// 			}
// 		});
// 	}

// 	load_data();
// 	setInterval(load_data, 30000);
// };
frappe.pages["site-activities"].on_page_load = function (wrapper) {

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Site Activities"),
		single_column: true
	});

	// PRINT BUTTON
	page.add_inner_button(__('Print'), () => {
		window.print();
	});

	// PRINT CSS
	if (!document.getElementById("site-activities-print-style")) {
		$(`<style id="site-activities-print-style">
		@media print {
			body * { visibility: hidden; }

			.page-content, .page-content * {
				visibility: visible;
			}

			.page-content {
				position: absolute;
				left: 0;
				top: 0;
				width: 100%;
			}

			.print-heading {
				display: block !important;
				text-align: center;
				font-size: 22px;
				font-weight: bold;
				margin-bottom: 20px;
			}

			table { border-collapse: collapse; }
			th, td { border: 1px solid #000 !important; }
		}

		.print-heading { display: none; }
		</style>`).appendTo("head");
	}

	const project = frappe.get_route()[1];

	if (!project) {
		page.body.html(`<div class="alert alert-warning">Project not specified</div>`);
		return;
	}

	const wrapper_el = $('<div class="mt-4"></div>').appendTo(page.body);

	// ------------------------------------------
	// MACHINERY (ORDER FIXED)
	// ------------------------------------------
	function build_machinery_table(data) {
		let rows = "";

		(data || []).forEach((d, i) => {
			rows += `
				<tr>
					<td>${i + 1}</td>
					<td>${d.description || ""}</td>
					<td>${d.size || ""}</td>
					<td>${d.area || ""}</td>
					<td>${d.no_on_site || ""}</td>
					<td>${d.down_time ? (d.down_time / 3600).toFixed(2) + " hrs" : ""}</td>
					<td>${d.total_working_hours || 0}</td>
					<td>${d.remarks || ""}</td>
				</tr>
			`;
		});

		return `
			<h4>Machinery & Equipments Used</h4>
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>No</th>
						<th>Description</th>
						<th>Size</th>
						<th>Area</th>
						<th>No. On Site</th>
						<th>Down Time</th>
						<th>Total Working Hours</th>
						<th>Remarks</th>
					</tr>
				</thead>
				<tbody>${rows || `<tr><td colspan="8">No data</td></tr>`}</tbody>
			</table>
		`;
	}

	// ------------------------------------------
	// MATERIALS (ORDER FIXED)
	// ------------------------------------------
	function build_materials_table(data) {
		let rows = "";

		(data || []).forEach((d) => {
			rows += `
				<tr>
					<td>${d.time || ""}</td>
					<td>${d.description || ""}</td>
					<td>${d.ticket_no || ""}</td>
					<td>${d.boq_no_pageitem_no || ""}</td>
					<td>${d.quantity || ""}</td>
					<td>${d.units || ""}</td>
					<td>${d.area || ""}</td>
					<td>${d.origin__manufacturer || ""}</td>
					<td>${d.remarks || ""}</td>
				</tr>
			`;
		});

		return `
			<h4>Materials Delivered to Site</h4>
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>Time</th>
						<th>Description</th>
						<th>Ticket No</th>
						<th>BOQ No</th>
						<th>Quantity</th>
						<th>Units</th>
						<th>Area</th>
						<th>Origin / Manufacturer</th>
						<th>Remarks</th>
					</tr>
				</thead>
				<tbody>${rows || `<tr><td colspan="9">No data</td></tr>`}</tbody>
			</table>
		`;
	}

	// ------------------------------------------
	// MANPOWER (CUSTOM ORDER FIXED)
	// ------------------------------------------
	function build_manpower_table(data) {
		let rows = "";

		(data || []).forEach((d) => {
			rows += `
				<tr>
					<td>${d.labor_occupation || ""}</td>
					<td>${d.staff || ""}</td>
					<td>${d.staff_occupation || ""}</td>
					<td>${d.skilled || ""}</td>
					<td>${d.unskilled || ""}</td>
					<td>${d.daily_total_units || ""}</td>
					<td>${d.hours || ""}</td>
				</tr>
			`;
		});

		return `
			<h4>Manpower Available at Site</h4>
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>Occupation</th>
						<th>Staff</th>
						<th>Occupation</th>
						<th>Skilled</th>
						<th>Unskilled</th>
						<th>Labor Units</th>
						<th>Labor Hours</th>
					</tr>
				</thead>
				<tbody>${rows || `<tr><td colspan="7">No data</td></tr>`}</tbody>
			</table>
		`;
	}

	// ------------------------------------------
	// ACTIVITIES (UNCHANGED)
	// ------------------------------------------
	function build_table(title, data, parent_minimal = false) {
		let body_html = "";

		(data || []).forEach(section => {
			const p = section.parent;

			body_html += `
				<tr class="table-active">
					<td></td>
					<td>${p.subject || ""}</td>
					<td>${p.custom_location || ""}</td>
					<td>${parent_minimal ? "" : (p.exp_start_date || "")}</td>
					<td>${parent_minimal ? "" : (p.exp_end_date || "")}</td>
					<td>${parent_minimal ? "" : (p.progress || 0) + "%"}</td>
					<td>${parent_minimal ? "" : (p.description || "")}</td>
				</tr>
			`;

			(section.children || []).forEach((t, i) => {
				body_html += `
					<tr>
						<td>${i + 1}</td>
						<td>${t.subject || ""}</td>
						<td>${t.custom_location || ""}</td>
						<td>${t.exp_start_date || ""}</td>
						<td>${t.exp_end_date || ""}</td>
						<td>${t.progress || 0}%</td>
						<td>${t.description || ""}</td>
					</tr>
				`;
			});
		});

		return `
			<h4>${title}</h4>
			<table class="table table-bordered">
				<thead>
					<tr>
						<th>#</th><th>Description</th><th>Area</th>
						<th>Start</th><th>End</th><th>%</th><th>Remarks</th>
					</tr>
				</thead>
				<tbody>${body_html || `<tr><td colspan="7">No data</td></tr>`}</tbody>
			</table>
		`;
	}

	// ------------------------------------------
	// LOAD DATA
	// ------------------------------------------
	function load_data() {
		frappe.call({
			method: "builder_erpgulf.builder_erpgulf.page.site_activities.site_activities.get_project_activities",
			args: { project },
			callback(r) {
				if (!r.message) return;

				wrapper_el.html(`
					<div class="print-heading">
						Site Activities - ${r.message.project_name || project}
					</div>

					${build_machinery_table(r.message.machinery)}
					${build_materials_table(r.message.materials)}
					${build_manpower_table(r.message.manpower)}

					${build_table("Activities in Progress", r.message.in_progress)}
					${build_table("Activities Planned for the Next Day", r.message.next_day, true)}
				`);
			}
		});
	}

	load_data();
	setInterval(load_data, 30000);
};