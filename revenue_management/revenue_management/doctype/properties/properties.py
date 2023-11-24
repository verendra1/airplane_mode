# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import numpy as np
import requests
import os
import pandas as pd
import sys
import traceback
from frappe.utils import cstr
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from revenue_management.utlis import dataimport, upload_file_api, get_cluster_details


class Properties(Document):
    pass


@frappe.whitelist()
def import_properties(file=None):
    try:
        if not file:
            return {"success": False, "message": "file is missing"}
        site_name = cstr(frappe.local.site)
        file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + file
        excel_data_df = pd.read_excel(file_path)
        if len(excel_data_df) == 0:
            frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "no data in the file", "file": cluser_file_upload["file"]})
            return {"success": False, "message": "No data in the file"}
        masha_details_columns = ["MARSHA", "Property Name on Tableau", "Status", "Area", "ADRS", "City",
                                 "Team Name", "Currency", "Country", "Market Share Type", "Market Share Comp", "Team Type", "Billing Unit"]
        if set(masha_details_columns).issubset(excel_data_df.columns):
            cluster_details = get_cluster_details()
            if not cluster_details["success"]:
                frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": cluster_details["message"], "file": cluser_file_upload["file"]})
                return cluster_details
            get_masha_list = frappe.db.get_list("Marsha Details", pluck="name")
            masha_details_df = excel_data_df[masha_details_columns]
            if len(masha_details_df) > 0:
                get_missing_cluster_properties = masha_details_df[~masha_details_df["Team Name"].isin(
                    cluster_details["data"])]
                if len(get_missing_cluster_properties) > 0:
                    missing_clusters_file = frappe.utils.get_bench_path() + "/sites/" + site_name + \
                        "/public/files/Missing Clusters.xlsx"
                    get_missing_cluster_properties.to_excel(
                        missing_clusters_file, index=False)
                    cluser_file_upload = upload_file_api(
                        filename=missing_clusters_file)
                    if not cluser_file_upload["success"]:
                        return cluser_file_upload
                    frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "missing cluster detials for some properties", "file": cluser_file_upload["file"]})
                    return {"success": False, "message": "missing cluster detials for some properties", "file": cluser_file_upload["file"]}
                # remove_missing_cluster_properties =  masha_details_df[masha_details_df["Team Name"].isin(cluster_details["data"])]
                remove_existing_masha_data_df = masha_details_df[~masha_details_df["MARSHA"].isin(
                    get_masha_list)]
                masha_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
                    "/public/files/Masha Details.csv"
                if len(remove_existing_masha_data_df) > 0:
                    remove_existing_masha_data_df.rename(
                        columns={"Team Name": "CLUSTER"}, inplace=True)
                    remove_existing_masha_data_df.to_csv(
                        masha_file_name, sep=',', index=False)

                    file_upload = upload_file_api(filename=masha_file_name)
                    if not file_upload["success"]:
                        return file_upload
                    dataimport(file=file_upload["file"], import_type="Insert New Records",
                               reference_doctype="Marsha Details")

                existing_masha_data_df = masha_details_df[masha_details_df["MARSHA"].isin(
                    get_masha_list)]
                if len(existing_masha_data_df) > 0:
                    existing_masha_data_df.rename(
                        columns={"Team Name": "CLUSTER"}, inplace=True)
                    existing_masha_data_df.to_csv(
                        masha_file_name, sep=',', index=False)

                    file_upload = upload_file_api(filename=masha_file_name)
                    if not file_upload["success"]:
                        return file_upload
                    dataimport(file=file_upload["file"], import_type="Update Existing Records",
                               reference_doctype="Marsha Details")
                return {"success": True, "message": "Data Imported"}
            frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "no data found", "file": ""})
            return {"success": False, "message": "No data found"}
        frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "file mismatch.", "file": ""})
        return {"success": False, "message": "Some columns are missing in excel file."}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("import_properties", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def import_properties_team_leaders(file=None):
    try:
        enqueue(
            import_properties,
            queue="long",
            timeout=800000,
            is_async=True,
            now=False,
            file=file,
            event="import_properties",
            job_name="Properties_Import"
        )
        return {"success": True, "Message": "Properties Import Starts Soon"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("import_properties_team_leaders", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}
