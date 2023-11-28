// Copyright (c) 2023, Caratred Technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Goals Vs Productivity"] = {
	"filters": [
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			default: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov","Dec"],
			options: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
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
