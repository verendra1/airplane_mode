// Copyright (c) 2023, Verendra and contributors
// For license information, please see license.txt

frappe.ui.form.on('Airline', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Airline', {
    refresh: function(frm) {
        frm.add_web_link(frm.doc.website,"View Website")
    }
});