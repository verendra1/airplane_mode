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
from revenue_management.utlis import dataimport


class Properties(Document):
    pass


@frappe.whitelist()
def import_properties_team_leaders(file=None):
    try:
        if not file:
            return {"success": False, "message": "file is missing"}
        site_name = cstr(frappe.local.site)
        file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + file
        excel_data_df = pd.read_excel(file_path)
        if len(excel_data_df) == 0:
            return {"success": False, "message": "No data in the file"}
        masha_details_columns = ["MARSHA", "Property Name on Tableau", "Status", "Area", "ADRS", "City",
                                 "Team Name", "Currency", "Country", "Market Share Type", "Market Share Comp", "Team Type", "Billing Unit"]
        if set(masha_details_columns).issubset(excel_data_df.columns):
            get_masha_list = frappe.db.get_list("Marsha Details", pluck="name")
            masha_details_df = excel_data_df[masha_details_columns]
            if len(masha_details_df) > 0:
                remove_existing_masha_data_df = masha_details_df[~masha_details_df["MARSHA"].isin(
                    get_masha_list)]
                masha_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
                    "/public/files/Masha Details.csv"
                if len(remove_existing_masha_data_df) > 0:
                    remove_existing_masha_data_df.rename(
                        columns={"Team Name": "CLUSTER"}, inplace=True)
                    remove_existing_masha_data_df.to_csv(
                        masha_file_name, sep=',', index=False)

                    files = {"file": open(masha_file_name, 'rb')}
                    payload = {'is_private': 1, 'folder': 'Home'}
                    upload_qr_image = requests.post("http://"+"0.0.0.0:8000" + "/api/method/upload_file",
                                                    files=files,
                                                    data=payload, verify=False)
                    response = upload_qr_image.json()
                    if 'message' in response:
                        os.remove(masha_file_name)
                        file = response['message']['file_url']
                        dataimport(file=file, import_type="Insert New Records",
                                   reference_doctype="Marsha Details")
                        if "success" in dataimport:
                            return dataimport
                    else:
                        return {"success": False, "message": response}

                existing_masha_data_df = masha_details_df[masha_details_df["MARSHA"].isin(
                    get_masha_list)]
                if len(existing_masha_data_df) > 0:
                    existing_masha_data_df.rename(
                        columns={"Team Name": "CLUSTER"}, inplace=True)
                    existing_masha_data_df.to_csv(
                        masha_file_name, sep=',', index=False)

                    files = {"file": open(masha_file_name, 'rb')}
                    payload = {'is_private': 1, 'folder': 'Home'}
                    upload_qr_image = requests.post("http://"+"0.0.0.0:8000" + "/api/method/upload_file",
                                                    files=files,
                                                    data=payload, verify=False)
                    response = upload_qr_image.json()
                    if 'message' in response:
                        os.remove(masha_file_name)
                        file = response['message']['file_url']
                        dataimport(file=file, import_type="Update Existing Records",
                                   reference_doctype="Marsha Details")
                        if "success" in dataimport:
                            return dataimport
                    else:
                        return {"success": False, "message": response}

        team_leader_details = ["Revenue Leader",
                               "EID", "Email Id", "Team Name", "MARSHA"]
        if set(team_leader_details).issubset(excel_data_df.columns):
            team_leader_list = frappe.db.get_list("Team Leaders", pluck="name")
            team_leaders_df = excel_data_df[team_leader_details]
            if len(team_leaders_df) > 0:
                remove_existing_team_leaders = team_leaders_df[~team_leaders_df["EID"].isin(
                    team_leader_list)]
                team_leader_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
                    "/public/files/Team Leaders.csv"
                if len(remove_existing_team_leaders) > 0:
                    sort_new_team_leaders = remove_existing_team_leaders.sort_values([
                                                                                     "Team Name"])
                    sort_new_team_leaders.rename(
                        columns={"MARSHA": "Marsha (Properties)", "Team Name": "Cluster"}, inplace=True)
                    remove_duplicate_values = [
                        "Revenue Leader", "EID", "Email Id", "Cluster"]
                    sort_new_team_leaders[remove_duplicate_values] = sort_new_team_leaders[remove_duplicate_values].where(
                        sort_new_team_leaders[remove_duplicate_values].apply(lambda x: x != x.shift()), '')
                    sort_new_team_leaders.loc[sort_new_team_leaders["Revenue Leader"].duplicated(
                    ), "Revenue Leader"] = np.NaN

                    sort_new_team_leaders.to_csv(
                        team_leader_file_name, index=False)

                    files = {"file": open(team_leader_file_name, 'rb')}
                    payload = {'is_private': 1, 'folder': 'Home'}
                    upload_qr_image = requests.post("http://"+"0.0.0.0:8000" + "/api/method/upload_file",
                                                    files=files,
                                                    data=payload, verify=False)
                    response = upload_qr_image.json()
                    if 'message' in response:
                        os.remove(team_leader_file_name)
                        file = response['message']['file_url']
                        dataimport(
                            file=file, import_type="Insert New Records", reference_doctype="Team Leaders")
                        if "success" in dataimport:
                            return dataimport
                    else:
                        return {"success": False, "message": response}

                existing_team_leader_data = team_leaders_df[team_leaders_df["EID"].isin(
                    team_leader_list)]
                if len(existing_team_leader_data) > 0:
                    sort_existing_team_leaders = existing_team_leader_data.sort_values([
                                                                                       "Team Name"])
                    sort_existing_team_leaders.rename(
                        columns={"MARSHA": "Marsha (Properties)", "Team Name": "Cluster"}, inplace=True)
                    sort_existing_team_leaders[remove_duplicate_values] = sort_existing_team_leaders[remove_duplicate_values].where(
                        sort_existing_team_leaders[remove_duplicate_values].apply(lambda x: x != x.shift()), '')
                    sort_existing_team_leaders.loc[sort_existing_team_leaders["Revenue Leader"].duplicated(
                    ), "Revenue Leader"] = np.NaN

                    sort_existing_team_leaders.to_csv(
                        team_leader_file_name, index=False)

                    files = {"file": open(team_leader_file_name, 'rb')}
                    payload = {'is_private': 1, 'folder': 'Home'}
                    upload_qr_image = requests.post("http://"+"0.0.0.0:8000" + "/api/method/upload_file",
                                                    files=files,
                                                    data=payload, verify=False)
                    response = upload_qr_image.json()
                    if 'message' in response:
                        os.remove(team_leader_file_name)
                        file = response['message']['file_url']
                        dataimport(
                            file=file, import_type="Insert New Records", reference_doctype="Team Leaders")
                        if "success" in dataimport:
                            return dataimport
                    else:
                        return {"success": False, "message": response}
        return {"success": True, "message": "Data Imported"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("import_properties_team_leaders", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}
