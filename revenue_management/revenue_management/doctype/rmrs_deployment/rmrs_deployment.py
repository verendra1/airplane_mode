# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


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


# @frappe.whitelist()
# def get_properties(deployment_type="",cluster_name="",property_name=""):
#     '''
#     get properties from marsha details based on cluster/Hotel
#     if customer choosed cluster return all marsha details under cluster
#         if customer selected individual hotel return singal marsha details

#     '''
#     try:
#         if deployment_type == 'Cluster':
#             marsha_details = frappe.db.get_list('Marsha Details', filters={
#                 'cluster': cluster_name,
#                 # 'fields':['*']
#             },)
#             return {"success":True,"data":marsha_details}

#         else:
#             marsha_details = frappe.db.get_list('Marsha Details', filters={
#                 'property_name': property_name,
#                 # 'fields':['*']
#             },)
#             return {"success":True,"data":marsha_details}

#     except Exception as e:
#         print(e)
#         return {"success":False,"data":{}}

