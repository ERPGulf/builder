

// frappe.query_reports["Site Activities Report"] = {

//     filters: [
//         {
//             fieldname: "project",
//             label: "Project",
//             fieldtype: "Link",
//             options: "Project",
//             reqd: 1
//         }
//     ],

//     onload: function (report) {
//         if (!document.getElementById("dcr-style")) {
//             const s = document.createElement("style");
//             s.id = "dcr-style";

//             s.textContent = `

//         /* =========================
//            MAIN CONTAINER
//         ==========================*/
//         #dcr-container{
//             width: 100%;
//             padding: 20px;
//             background: #fff;
//             font-family: Arial, Helvetica, sans-serif;
//             color: #222;
//             font-size: 12px;
//         }

//         #dcr-container table{
//             width: 100%;
//             border-collapse: collapse;
//         }

//         #dcr-container td,
//         #dcr-container th{
//             border: 1px solid #444;
//             padding: 6px 8px;
//             vertical-align: middle;
//         }

//         /* =========================
//            HEADER SECTION
//         ==========================*/
//         #dcr-container .tr-project td{
//             background: #fff;
//             color: #222;
//             border: 2px solid #444;
//             padding: 10px 18px;
//         }

//         /* Logo row: client logo left, TDI logo right */
//         #dcr-container .logo-row{
//             display: flex;
//             justify-content: space-between;
//             align-items: center;
//             margin-bottom: 16px;
//         }

//         #dcr-container .logo-row .logo-left,
//         #dcr-container .logo-row .logo-right{
//             display: flex;
//             align-items: center;
//             justify-content: center;
//             min-width: 120px;
//         }

//         #dcr-container .logo-row .logo-center{
//             flex: 1;
//             text-align: center;
//         }

//         #dcr-container .logo-row img{
//             height: 80px;
//             width: auto;
//             object-fit: contain;
//         }

//         #dcr-container .logo-placeholder{
//             height: 80px;
//             width: 120px;
//             display: flex;
//             align-items: center;
//             justify-content: center;
//             border: 1px dashed #ccc;
//             color: #bbb;
//             font-size: 11px;
//             border-radius: 4px;
//         }

//         #dcr-container .report-main-title{
//             font-size: 20px;
//             font-weight: 700;
//             letter-spacing: 1px;
//             color: #222;
//         }

//         #dcr-container .report-sub-title{
//             font-size: 12px;
//             color: #555;
//             margin-top: 4px;
//         }

//         #dcr-container .hgrid{
//             display: grid;
//             grid-template-columns: 1fr 1fr;
//             gap: 10px 30px;
//             align-items: center;
//             margin-top: 10px;
//         }

//         #dcr-container .hgrid div{
//             font-size: 12px;
//         }

//         #dcr-container .hlabel{
//             font-weight: bold;
//             margin-right: 6px;
//         }

//         #dcr-container .info-row{
//             display: flex;
//             align-items: center;
//             gap: 12px;
//             margin-bottom: 10px;
//         }

//         #dcr-container .info-label{
//             min-width: 120px;
//             font-weight: bold;
//         }

//         #dcr-container .info-value{
//             font-weight: normal;
//         }

//         #dcr-container .company-box{
//             text-align: center;
//         }

//         #dcr-container .company-title{
//             font-size: 14px;
//             font-weight: bold;
//             margin-bottom: 8px;
//         }

//         #dcr-container .company-logo{
//             width: 140px;
//             height: auto;
//             object-fit: contain;
//         }

//         /* =========================
//            PROJECT INFO
//         ==========================*/
//         #dcr-container .project-info{
//             margin-top: 14px;
//             margin-bottom: 10px;
//         }

//         #dcr-container .project-info table{
//             border: none;
//         }

//         #dcr-container .project-info td{
//             border: none;
//             padding: 2px 4px;
//             font-size: 13px;
//         }

//         #dcr-container .project-label{
//             width: 130px;
//             font-weight: bold;
//         }

//         #dcr-container .dcr-title{
//             text-align: center;
//             font-size: 28px;
//             font-weight: 700;
//             margin: 18px 0;
//             letter-spacing: 1px;
//         }

//         /* =========================
//            META SECTION
//         ==========================*/
//         #dcr-container .meta-table{
//             width: 100%;
//             margin-bottom: 14px;
//         }

//         #dcr-container .meta-table td{
//             border: none;
//             padding: 4px 6px;
//             font-size: 13px;
//         }

//         #dcr-container .meta-label{
//             font-weight: bold;
//             width: 90px;
//         }

//         /* =========================
//            SECTION TITLE
//         ==========================*/
//         #dcr-container .tr-section td{
//             background: #9fc5e8;
//             color: #111;
//             font-weight: bold;
//             font-size: 14px;
//             padding: 8px 10px;
//             border: 1px solid #444;
//         }

//         /* =========================
//            COLUMN HEADERS
//         ==========================*/
//         #dcr-container .tr-cols th{
//             background: #efefef;
//             color: #111;
//             font-size: 12px;
//             font-weight: bold;
//             text-align: center;
//             border: 1px solid #444;
//             padding: 6px;
//         }

//         /* =========================
//            DATA ROWS
//         ==========================*/
//         #dcr-container .tr-data td,
//         #dcr-container .tr-act-parent td,
//         #dcr-container .tr-act-child td{
//             background: #fff;
//             color: #222;
//             font-size: 12px;
//             border: 1px solid #444;
//             height: 28px;
//         }

//         #dcr-container .tr-data:nth-child(even) td{
//             background: #fafafa;
//         }

//         /* =========================
//            EMPTY ROWS
//         ==========================*/
//         #dcr-container .tr-empty td{
//             height: 28px;
//             color: #999;
//             font-style: italic;
//             text-align: center;
//         }

//         /* =========================
//            PRINT
//         ==========================*/
//         @media print {

//             body{
//                 background: #fff;
//             }

//             .page-head,
//             .page-form,
//             .page-actions,
//             .navbar{
//                 display:none !important;
//             }

//             #dcr-container{
//                 padding: 0;
//                 margin: 0;
//             }

//             #dcr-container .tr-section td{
//                 background:#9fc5e8 !important;
//                 -webkit-print-color-adjust: exact;
//             }

//             #dcr-container .tr-cols th{
//                 background:#efefef !important;
//                 -webkit-print-color-adjust: exact;
//             }

//             #dcr-container .logo-placeholder{
//                 display: none;
//             }
//         }

//         `;

//             document.head.appendChild(s);
//         }

//         report.page.add_inner_button(__("Print"), () => window.print());
//     },

//     after_datatable_render: function (dt) {
//         const data = frappe.query_report.data || [];
//         if (!data.length) return;

//         const $wrap = $(dt.wrapper);
//         $wrap.find(".dt-scrollable, .dt-header, .dt-footer").hide();
//         $wrap.find("#dcr-container").remove();

//         const v = (row, k) =>
//             (row[k] != null && row[k] !== "")
//                 ? String(row[k]).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
//                 : "&ndash;";

//         // ── Column definitions ───────────────────────────────────
//         const MACHINERY_COLS = [
//             { h: "#", k: "no" },
//             { h: "Description", k: "description" },
//             { h: "Size", k: "size" },
//             { h: "Area", k: "area" },
//             { h: "No. On Site", k: "no_on_site" },
//             { h: "Down Time", k: "down_time" },
//             { h: "Total Working Hrs", k: "total_hours" },
//             { h: "Remarks", k: "remarks" },
//         ];

//         const MATERIAL_COLS = [
//             { h: "Time", k: "time" },
//             { h: "Description", k: "description" },
//             { h: "Ticket No", k: "ticket_no" },
//             { h: "BOQ No / Page Item No", k: "boq_no" },
//             { h: "Quantity", k: "quantity" },
//             { h: "Units", k: "units" },
//             { h: "Area", k: "area" },
//             { h: "Origin / Manufacturer", k: "origin" },
//             { h: "Remarks", k: "remarks" },
//         ];

//         const MANPOWER_COLS = [
//             { h: "Occupation", k: "labor_occupation" },
//             { h: "Staff", k: "staff" },
//             { h: "Occupation", k: "staff_occupation" },
//             { h: "Skilled", k: "skilled" },
//             { h: "Unskilled", k: "unskilled" },
//             { h: "Labor Units", k: "daily_total_units" },
//             { h: "Labor Hours", k: "hours" },
//         ];

//         const ACTIVITY_COLS = [
//             { h: "#", k: "act_no" },
//             { h: "Description", k: "description" },
//             { h: "Area", k: "area" },
//             { h: "Start", k: "date_started" },
//             { h: "End", k: "date_ended" },
//             { h: "%", k: "pct" },
//             { h: "Remarks", k: "remarks" },
//         ];

//         const MAX_COLS = Math.max(
//             MACHINERY_COLS.length,
//             MATERIAL_COLS.length,
//             MANPOWER_COLS.length,
//             ACTIVITY_COLS.length
//         );

//         let html = `<div id="dcr-container"><table>`;
//         let currentCols = [];
//         let rowIdx = 0;

//         // ── Helpers ──────────────────────────────────────────────
//         function sectionBanner(cols, title) {
//             currentCols = cols;
//             rowIdx = 0;
//             const pad = MAX_COLS - cols.length;
//             html += `
//             <tr class="tr-section">
//                 <td colspan="${MAX_COLS}">${title}</td>
//             </tr>
//             <tr class="tr-cols">
//                 ${cols.map(c => `<th>${c.h}</th>`).join("")}
//                 ${pad > 0 ? `<th colspan="${pad}"></th>` : ""}
//             </tr>`;
//         }

//         function dataRow(cols, row, trClass) {
//             const even = (rowIdx % 2 === 1) ? " even" : "";
//             const pad = MAX_COLS - cols.length;
//             rowIdx++;
//             html += `
//             <tr class="${trClass}${even}">
//                 ${cols.map(c => `<td>${v(row, c.k)}</td>`).join("")}
//                 ${pad > 0 ? `<td colspan="${pad}"></td>` : ""}
//             </tr>`;
//         }

//         // ── Render rows ──────────────────────────────────────────
//         data.forEach(row => {
//             const s = row.section;

//             if (s === "HEADER") {

//                 // Build client logo HTML (left side)
//                 const clientLogoUrl = (row.client_logo && row.client_logo !== "&ndash;")
//                     ? row.client_logo
//                     : null;

//                 const clientLogoHtml = clientLogoUrl
//                     ? `<img src="${clientLogoUrl}" alt="Client Logo" />`
//                     : `<div class="logo-placeholder">No Client Logo</div>`;

//                 html += `
//                 <tr class="tr-project">
//                     <td colspan="${MAX_COLS}">

//                         <!-- ── Logo Row ── -->
//                         <div class="logo-row">
//                             <!-- Client logo LEFT -->
//                             <div class="logo-left">
//                                 ${clientLogoHtml}
//                             </div>

//                             <!-- Center title -->
//                             <div class="logo-center">
//                                 <div class="report-main-title">DAILY CONSTRUCTION REPORT</div>
//                                 <div class="report-sub-title">Site Activities Report</div>
//                             </div>

//                             <!-- TDI logo RIGHT -->
//                             <div class="logo-right">
//                                 <img src="/files/TDI Logo.jpeg" alt="TDI Logo" />
//                             </div>
//                         </div>

//                         <!-- ── Project Info Grid ── -->
//                         <div class="hgrid">
//                             <div><span class="hlabel">Project Ref:</span>${v(row, "project_ref")}</div>
//                             <div><span class="hlabel">Project Name:</span>${v(row, "project_name")}</div>
//                             <div><span class="hlabel">Company:</span>${v(row, "company")}</div>
//                             <div><span class="hlabel">Status:</span>${v(row, "status")}</div>
//                             <div><span class="hlabel">Priority:</span>${v(row, "priority")}</div>
//                             <div><span class="hlabel">% Complete:</span>${v(row, "percent_complete")}%</div>
//                         </div>

//                     </td>
//                 </tr>`;
//                 return;
//             }

//             if (s === "MACHINERY_HEADER") { sectionBanner(MACHINERY_COLS, "Machinery &amp; Equipments Used"); return; }
//             if (s === "MACHINERY") { dataRow(currentCols, row, "tr-data"); return; }

//             if (s === "MATERIAL_HEADER") { sectionBanner(MATERIAL_COLS, "Materials Delivered to Site"); return; }
//             if (s === "MATERIAL") { dataRow(currentCols, row, "tr-data"); return; }

//             if (s === "MANPOWER_HEADER") { sectionBanner(MANPOWER_COLS, "Manpower Available at Site"); return; }
//             if (s === "MANPOWER") { dataRow(currentCols, row, "tr-data"); return; }

//             if (s === "INPROGRESS_HEADER") { sectionBanner(ACTIVITY_COLS, "Activities in Progress"); return; }
//             if (s === "NEXTDAY_HEADER") { sectionBanner(ACTIVITY_COLS, "Activities Planned for the Next Day"); return; }

//             if (s === "ACTIVITY_PARENT") {
//                 const pad = MAX_COLS - ACTIVITY_COLS.length;
//                 html += `
//                 <tr class="tr-act-parent">
//                     ${ACTIVITY_COLS.map(c => `<td>${v(row, c.k)}</td>`).join("")}
//                     ${pad > 0 ? `<td colspan="${pad}"></td>` : ""}
//                 </tr>`;
//                 return;
//             }

//             if (s === "ACTIVITY_CHILD" || s === "NEXTDAY_CHILD") {
//                 dataRow(ACTIVITY_COLS, row, "tr-act-child");
//                 return;
//             }

//             if (s === "NEXTDAY_EMPTY") {
//                 html += `
//                 <tr class="tr-empty">
//                     <td colspan="${MAX_COLS}">No data</td>
//                 </tr>`;
//                 return;
//             }
//         });

//         html += `</table></div>`;
//         $wrap.find(".dt-scrollable").after($(html));
//     }
// };
frappe.query_reports["Site Activities Report"] = {

    filters: [
        {
            fieldname: "project",
            label: "Project",
            fieldtype: "Link",
            options: "Project",
            reqd: 1
        }
    ],

    onload: function (report) {
        if (!document.getElementById("dcr-style")) {
            const s = document.createElement("style");
            s.id = "dcr-style";

            s.textContent = `

        /* =========================
           MAIN CONTAINER
        ==========================*/
        #dcr-container{
            width: 100%;
            padding: 20px;
            background: #fff;
            font-family: Arial, Helvetica, sans-serif;
            color: #222;
            font-size: 12px;
        }

        #dcr-container table{
            width: 100%;
            border-collapse: collapse;
        }

        #dcr-container td,
        #dcr-container th{
            border: 1px solid #444;
            padding: 6px 8px;
            vertical-align: middle;
        }

        /* =========================
           HEADER SECTION
        ==========================*/
        #dcr-container .tr-project td{
            background: #fff;
            color: #222;
            border: 2px solid #444;
            padding: 10px 18px;
        }

        #dcr-container .logo-row{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        #dcr-container .logo-row .logo-left,
        #dcr-container .logo-row .logo-right{
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 120px;
        }

        #dcr-container .logo-row .logo-center{
            flex: 1;
            text-align: center;
        }

        #dcr-container .logo-row img{
            height: 80px;
            width: auto;
            object-fit: contain;
        }

        #dcr-container .logo-placeholder{
            height: 80px;
            width: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px dashed #ccc;
            color: #bbb;
            font-size: 11px;
            border-radius: 4px;
        }

        #dcr-container .report-main-title{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: 1px;
            color: #222;
        }

        #dcr-container .report-sub-title{
            font-size: 12px;
            color: #555;
            margin-top: 4px;
        }

        #dcr-container .hgrid{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px 30px;
            align-items: center;
            margin-top: 10px;
        }

        #dcr-container .hgrid div{
            font-size: 12px;
        }

        #dcr-container .hlabel{
            font-weight: bold;
            margin-right: 6px;
        }

        #dcr-container .info-row{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }

        #dcr-container .info-label{
            min-width: 120px;
            font-weight: bold;
        }

        #dcr-container .info-value{
            font-weight: normal;
        }

        #dcr-container .company-box{
            text-align: center;
        }

        #dcr-container .company-title{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        #dcr-container .company-logo{
            width: 140px;
            height: auto;
            object-fit: contain;
        }

        /* =========================
           PROJECT INFO
        ==========================*/
        #dcr-container .project-info{
            margin-top: 14px;
            margin-bottom: 10px;
        }

        #dcr-container .project-info table{
            border: none;
        }

        #dcr-container .project-info td{
            border: none;
            padding: 2px 4px;
            font-size: 13px;
        }

        #dcr-container .project-label{
            width: 130px;
            font-weight: bold;
        }

        #dcr-container .dcr-title{
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            margin: 18px 0;
            letter-spacing: 1px;
        }

        /* =========================
           META SECTION
        ==========================*/
        #dcr-container .meta-table{
            width: 100%;
            margin-bottom: 14px;
        }

        #dcr-container .meta-table td{
            border: none;
            padding: 4px 6px;
            font-size: 13px;
        }

        #dcr-container .meta-label{
            font-weight: bold;
            width: 90px;
        }

        /* =========================
           SECTION TITLE
        ==========================*/
        #dcr-container .tr-section td{
            background: #9fc5e8;
            color: #111;
            font-weight: bold;
            font-size: 14px;
            padding: 8px 10px;
            border: 1px solid #444;
        }

        /* =========================
           COLUMN HEADERS
        ==========================*/
        #dcr-container .tr-cols th{
            background: #efefef;
            color: #111;
            font-size: 12px;
            font-weight: bold;
            text-align: center;
            border: 1px solid #444;
            padding: 6px;
        }

        /* =========================
           DATA ROWS
        ==========================*/
        #dcr-container .tr-data td,
        #dcr-container .tr-act-parent td,
        #dcr-container .tr-act-child td{
            background: #fff;
            color: #222;
            font-size: 12px;
            border: 1px solid #444;
            height: 28px;
        }

        #dcr-container .tr-data:nth-child(even) td{
            background: #fafafa;
        }

        /* =========================
           EMPTY ROWS
        ==========================*/
        #dcr-container .tr-empty td{
            height: 28px;
            color: #999;
            font-style: italic;
            text-align: center;
        }

        /* =========================
           PRINT
        ==========================*/
        @media print {

            body{
                background: #fff;
            }

            .page-head,
            .page-form,
            .page-actions,
            .navbar{
                display:none !important;
            }

            #dcr-container{
                padding: 0;
                margin: 0;
            }

            #dcr-container .tr-section td{
                background:#9fc5e8 !important;
                -webkit-print-color-adjust: exact;
            }

            #dcr-container .tr-cols th{
                background:#efefef !important;
                -webkit-print-color-adjust: exact;
            }

            #dcr-container .logo-placeholder{
                display: none;
            }
        }

        `;

            document.head.appendChild(s);
        }

        report.page.add_inner_button(__("Print"), () => window.print());
    },

    after_datatable_render: function (dt) {
        const data = frappe.query_report.data || [];
        if (!data.length) return;

        const $wrap = $(dt.wrapper);
        $wrap.find(".dt-scrollable, .dt-header, .dt-footer").hide();
        $wrap.find("#dcr-container").remove();

        const v = (row, k) =>
            (row[k] != null && row[k] !== "")
                ? String(row[k]).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
                : "&ndash;";

        // ── Column definitions ───────────────────────────────────
        const MACHINERY_COLS = [
            { h: "#", k: "no" },
            { h: "Description", k: "description" },
            { h: "Size", k: "size" },
            { h: "Area", k: "area" },
            { h: "No. On Site", k: "no_on_site" },
            { h: "Down Time", k: "down_time" },
            { h: "Total Working Hrs", k: "total_hours" },
            { h: "Remarks", k: "remarks" },
        ];

        const MATERIAL_COLS = [
            { h: "Time", k: "time" },
            { h: "Description", k: "description" },
            { h: "Ticket No", k: "ticket_no" },
            { h: "BOQ No / Page Item No", k: "boq_no" },
            { h: "Quantity", k: "quantity" },
            { h: "Units", k: "units" },
            { h: "Area", k: "area" },
            { h: "Origin / Manufacturer", k: "origin" },
            { h: "Remarks", k: "remarks" },
        ];

        const MANPOWER_COLS = [
            { h: "Occupation", k: "labor_occupation" },
            { h: "Staff", k: "staff" },
            { h: "Occupation", k: "staff_occupation" },
            { h: "Skilled", k: "skilled" },
            { h: "Unskilled", k: "unskilled" },
            { h: "Labor Units", k: "daily_total_units" },
            { h: "Labor Hours", k: "hours" },
        ];

        const ACTIVITY_COLS = [
            { h: "#", k: "act_no" },
            { h: "Description", k: "description" },
            { h: "Area", k: "area" },
            { h: "Start", k: "date_started" },
            { h: "End", k: "date_ended" },
            { h: "%", k: "pct" },
            { h: "Remarks", k: "remarks" },
        ];

        // ── Issues: 2 cols only ──────────────────────────────────
        const ISSUES_COLS = [
            { h: "#", k: "no" },
            { h: "Issues", k: "issues" },
        ];

        const MAX_COLS = Math.max(
            MACHINERY_COLS.length,
            MATERIAL_COLS.length,
            MANPOWER_COLS.length,
            ACTIVITY_COLS.length,
            ISSUES_COLS.length
        );

        let html = `<div id="dcr-container"><table>`;
        let currentCols = [];
        let rowIdx = 0;

        // ── Helpers ──────────────────────────────────────────────
        function sectionBanner(cols, title) {
            currentCols = cols;
            rowIdx = 0;
            const pad = MAX_COLS - cols.length;
            html += `
            <tr class="tr-section">
                <td colspan="${MAX_COLS}">${title}</td>
            </tr>
            <tr class="tr-cols">
                ${cols.map(c => `<th>${c.h}</th>`).join("")}
                ${pad > 0 ? `<th colspan="${pad}"></th>` : ""}
            </tr>`;
        }

        function dataRow(cols, row, trClass) {
            const even = (rowIdx % 2 === 1) ? " even" : "";
            const pad = MAX_COLS - cols.length;
            rowIdx++;
            html += `
            <tr class="${trClass}${even}">
                ${cols.map(c => `<td>${v(row, c.k)}</td>`).join("")}
                ${pad > 0 ? `<td colspan="${pad}"></td>` : ""}
            </tr>`;
        }

        // ── Render rows ──────────────────────────────────────────
        data.forEach(row => {
            const s = row.section;

            if (s === "HEADER") {
                const clientLogoUrl = (row.client_logo && row.client_logo !== "&ndash;")
                    ? row.client_logo
                    : null;

                const clientLogoHtml = clientLogoUrl
                    ? `<img src="${clientLogoUrl}" alt="Client Logo" />`
                    : `<div class="logo-placeholder">No Client Logo</div>`;

                html += `
                <tr class="tr-project">
                    <td colspan="${MAX_COLS}">

                        <div class="logo-row">
                            <div class="logo-left">
                                ${clientLogoHtml}
                            </div>
                            <div class="logo-center">
                                <div class="report-main-title">DAILY CONSTRUCTION REPORT</div>
                                <div class="report-sub-title">Site Activities Report</div>
                            </div>
                            <div class="logo-right">
                                <img src="/files/TDI Logo.jpeg" alt="TDI Logo" />
                            </div>
                        </div>

                        <div class="hgrid">
                            <div><span class="hlabel">Project Ref:</span>${v(row, "project_ref")}</div>
                            <div><span class="hlabel">Project Name:</span>${v(row, "project_name")}</div>
                            <div><span class="hlabel">Company:</span>${v(row, "company")}</div>
                            <div><span class="hlabel">Status:</span>${v(row, "status")}</div>
                            <div><span class="hlabel">Priority:</span>${v(row, "priority")}</div>
                            <div><span class="hlabel">% Complete:</span>${v(row, "percent_complete")}%</div>
                        </div>

                    </td>
                </tr>`;
                return;
            }

            if (s === "MACHINERY_HEADER") { sectionBanner(MACHINERY_COLS, "Machinery &amp; Equipments Used"); return; }
            if (s === "MACHINERY") { dataRow(currentCols, row, "tr-data"); return; }

            if (s === "MATERIAL_HEADER") { sectionBanner(MATERIAL_COLS, "Materials Delivered to Site"); return; }
            if (s === "MATERIAL") { dataRow(currentCols, row, "tr-data"); return; }

            if (s === "MANPOWER_HEADER") { sectionBanner(MANPOWER_COLS, "Manpower Available at Site"); return; }
            if (s === "MANPOWER") { dataRow(currentCols, row, "tr-data"); return; }

            if (s === "INPROGRESS_HEADER") { sectionBanner(ACTIVITY_COLS, "Activities in Progress"); return; }
            if (s === "NEXTDAY_HEADER") { sectionBanner(ACTIVITY_COLS, "Activities Planned for the Next Day"); return; }

            if (s === "ACTIVITY_PARENT") {
                const pad = MAX_COLS - ACTIVITY_COLS.length;
                html += `
                <tr class="tr-act-parent">
                    ${ACTIVITY_COLS.map(c => `<td>${v(row, c.k)}</td>`).join("")}
                    ${pad > 0 ? `<td colspan="${pad}"></td>` : ""}
                </tr>`;
                return;
            }

            if (s === "ACTIVITY_CHILD" || s === "NEXTDAY_CHILD") {
                dataRow(ACTIVITY_COLS, row, "tr-act-child");
                return;
            }

            if (s === "NEXTDAY_EMPTY") {
                html += `
                <tr class="tr-empty">
                    <td colspan="${MAX_COLS}">No data</td>
                </tr>`;
                return;
            }

            // ── ISSUES ───────────────────────────────────────────
            if (s === "ISSUES_HEADER") { sectionBanner(ISSUES_COLS, "Issues"); return; }

            if (s === "ISSUE") { dataRow(currentCols, row, "tr-data"); return; }

            if (s === "ISSUES_EMPTY") {
                html += `
                <tr class="tr-empty">
                    <td colspan="${MAX_COLS}">No issues</td>
                </tr>`;
                return;
            }
        });

        html += `</table></div>`;
        $wrap.find(".dt-scrollable").after($(html));
    }
};