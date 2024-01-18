# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RMRSDeployment(Document):
	pass


def update_name_field(doc, method=None):
	try:
		if doc.deployment_type == "Cluster":
			doc.hotel_cluster_name = doc.cluster_name
		if doc.deployment_type == "Individual Property":
			doc.hotel_cluster_name = doc.hotel_name
		print(doc.hotel_cluster_name)
	except Exception as e:
		frappe.log_error(str(e), "update_name_field")