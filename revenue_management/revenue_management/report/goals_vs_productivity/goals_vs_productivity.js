// Copyright (c) 2023, Caratred Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Goals Vs Productivity"] = {
	"filters": [
		{
			fieldname: "marsha",
			label: __("Marsha"),
			fieldtype: "Link",
			options: "Marsha Details",
			"reqd": 1,
		},
		{
			fieldname: "quarter",
			label: __("Quarter"),
			fieldtype: "Select",
			default: ["Q1", "Q2", "Q3", "Q4"],
			options: ["Q1", "Q2", "Q3", "Q4"],
			"reqd": 1
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Data",
			"reqd": 1
		},

	]
};
