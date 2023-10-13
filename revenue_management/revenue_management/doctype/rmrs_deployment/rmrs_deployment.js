// Copyright (c) 2023, Caratred Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('RMRS Deployment', {
	refresh: function(frm) {
		console.log("Triggred")
	},
	deployement_type:function(frm){
		

	},
	cluster_name:function(frm){
		if (frm.doc.deployment_type){
			frm.doc.hotel_name = ''
			get_details(frm)
			
		}
	},
	hotel_name:function(frm){
		if (frm.doc.deployment_type){
			frm.doc.cluster_name = ''
			get_details(frm)

		}
	},
});

function reset_child_table_data(frm){

}


function get_details(frm){
	let child_table = frm.doc.properties;
	if (child_table){
		for (var i = 0; i < child_table.length; i++) {
			frappe.model.clear_doc(child_table[i].doctype, child_table[i].name);
		}
	}
	
	// Refresh the form to reflect the changes
	frm.refresh();

	if (frm.doc.cluster_name != ''){
		frappe.db.get_list(
			"Marsha Details", {
				filters:{'cluster': frm.doc.cluster_name}, 
				fields:['name','property_name','cluster','region',
				'city','currency','area','sub_region','country']}
		).then((res) => {
			res.forEach((marsha) => {
				// options.push(party_type.name);
				var child = frm.add_child("properties");
				child.marsha = marsha.name;
				child.property_name = marsha.property_name;
				child.currency = marsha.currency;

			});
			refresh_field("properties");

		});
	}else{
		frappe.db.get_list(
			"Marsha Details", {
				filters:{'name': frm.doc.hotel_name}, 
				fields:['name','property_name','cluster','region',
				'city','currency','area','sub_region','country']}
		).then((res) => {
			res.forEach((marsha) => {
					var child = frm.add_child("properties");
				 	child.marsha = marsha.name;
				 	child.property_name = marsha.property_name;
					 child.currency = marsha.currency;


	
			});
			refresh_field("properties");

		});
	}
	
}
