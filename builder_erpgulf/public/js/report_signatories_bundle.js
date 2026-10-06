window.__report_signatories_loaded = true;

const SIG_KEY = "report_signatories";
const sig_state = { ids: {}, data: {}, pending: {}, active: false };

function sig_saved() {
    try {
        return JSON.parse(localStorage.getItem(SIG_KEY)) || {};
    } catch (e) {
        return {};
    }
}

function sig_fetch(key, emp) {
    sig_state.ids[key] = emp || "";
    if (!emp) {
        sig_state.data[key] = null;
        return;
    }
    sig_state.pending[key] = frappe.db
        .get_value("Employee", emp, ["employee_name", "designation"])
        .then((r) => (sig_state.data[key] = r.message || null))
        .catch(() => (sig_state.data[key] = null));
}

function sig_applies(opts) {
    return (
        frappe.get_route()?.[0] === "query-report" &&
        opts &&
        Array.isArray(opts.fields) &&
        opts.fields.some((f) => f.fieldname === "orientation") &&
        !opts.fields.some((f) => f.fieldname === "prepared_by")
    );
}

function sig_patch(opts) {
    const saved = sig_saved();
    sig_state.data = {};
    sig_fetch("prepared_by", saved.prepared_by);
    sig_fetch("approved_by", saved.approved_by);

    opts.fields = [
        ...opts.fields,
        { fieldtype: "Section Break", label: __("Signatories") },
        {
            fieldname: "prepared_by",
            label: __("Prepared By"),
            fieldtype: "Link",
            options: "Employee",
            default: saved.prepared_by,
            onchange: function () {
                sig_fetch("prepared_by", this.get_value());
            },
        },
        { fieldtype: "Column Break" },
        {
            fieldname: "approved_by",
            label: __("Approved By"),
            fieldtype: "Link",
            options: "Employee",
            default: saved.approved_by,
            onchange: function () {
                sig_fetch("approved_by", this.get_value());
            },
        },
    ];

    const original_action = opts.primary_action;
    opts.primary_action = async function (...args) {
        await Promise.all(Object.values(sig_state.pending));
        localStorage.setItem(SIG_KEY, JSON.stringify(sig_state.ids));
        sig_state.active = true;
        return original_action && original_action.apply(this, args);
    };

    return opts;
}

const SigOriginalDialog = frappe.ui.Dialog;
frappe.ui.Dialog = class extends SigOriginalDialog {
    constructor(opts) {
        if (sig_applies(opts)) opts = sig_patch(opts);
        super(opts);
    }
};

function sig_html() {
    const esc = (v) => frappe.utils.escape_html(v || "");
    const pb = sig_state.data.prepared_by || {};
    const ab = sig_state.data.approved_by || {};

    return `
	<table style="width:100%; margin-top:40px; border:none; page-break-inside:avoid;">
		<tr>
			<td style="width:50%; border:none; vertical-align:top;">
				<div style="font-weight:bold;">PREPARED BY</div>
				<div style="margin-top:35px; border-top:1px solid #000; width:60%;"></div>
				<div>${esc(pb.employee_name)}</div>
				<div>${esc(pb.designation)}</div>
			</td>
			<td style="width:50%; border:none; vertical-align:top; text-align:right;">
				<div style="font-weight:bold;">APPROVED BY</div>
				<div style="margin-top:35px; border-top:1px solid #000; width:60%; margin-left:auto;"></div>
				<div>${esc(ab.employee_name)}</div>
				<div>${esc(ab.designation)}</div>
			</td>
		</tr>
	</table>`;
}

const sig_original_render_template = frappe.render_template;
frappe.render_template = function (name, data, ...rest) {
    if (name === "print_template" && sig_state.active && data) {
        sig_state.active = false;
        data = { ...data, content: (data.content || "") + sig_html() };
    }
    return sig_original_render_template.call(this, name, data, ...rest);
};