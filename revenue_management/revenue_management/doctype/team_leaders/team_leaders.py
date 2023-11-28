# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import sys
import traceback
import numpy as np
import pandas as pd
from frappe.utils import cstr
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from revenue_management.utlis import dataimport, upload_file_api, create_user, send_mail_to_user
from revenue_management.revenue_management.doctype.team_roster.team_roster import create_team


class TeamLeaders(Document):
    pass


def create_team_leader_as_user(doc, method=None):
    try:
        user_creation = create_user(email=doc.email_id, user_name=doc.eid,
                                    first_name=doc.revenue_leader, last_name=None, role="Team Lead")
        if not user_creation["success"]:
            return user_creation
        user_doc = frappe.get_doc("User", doc.email_id)
        if user_doc:
            b2csuccess = frappe.get_doc(
                'Email Template', "Team Leader Login Details")
            message = b2csuccess.response
            replace_first_name = message.replace(
                "[first_name]", user_doc.first_name)
            replace_email = replace_first_name.replace(
                "[email_id]", user_doc.email)
            send_mail_to_user(
                content=replace_email, email_id=user_doc.email, subject=b2csuccess.subject)
        create_team(doc.as_dict())
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_team_leader_as_user", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def import_team_leader(file=None):
    try:
        if not file:
            frappe.publish_realtime("data_import_error", {"data_import": 'Team Leader',"show_message": "file is missing in filters", "file": ""})
            return {"success": False, "message": "file is missing in filters"}
        site_name = cstr(frappe.local.site)
        file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + file
        excel_data_df = pd.read_excel(file_path)
        if len(excel_data_df) == 0:
            frappe.publish_realtime("data_import_error", {"data_import": 'Team Leader',"show_message": "no data in the file", "file": ""})
            return {"success": False, "message": "No data in the file"}

        team_leader_details = ["Revenue Leader",
                               "EID", "Email Id", "Team Name", "MARSHA"]
        if set(team_leader_details).issubset(excel_data_df.columns):
            get_employee_details = frappe.db.get_list(
                "Employees", pluck="name")
            team_leader_list = frappe.db.get_list("Team Leaders", pluck="name")
            team_leaders_df = excel_data_df[team_leader_details]
            team_leaders_df["EID"] = team_leaders_df["EID"].astype(str)

            # TeamLeader not there employee doctype conditon
            get_team_leader_not_in_employee = team_leaders_df[~team_leaders_df["EID"].isin(
                get_employee_details)]
            if len(get_team_leader_not_in_employee) > 0:
                missing_employee_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
                    "/public/files/Missing in employees.csv"
                get_team_leader_not_in_employee.to_csv(
                    missing_employee_file_name, index=False)

                fileupload = upload_file_api(
                    filename=missing_employee_file_name)
                if not fileupload["success"]:
                    return fileupload
                missing_employee_file = fileupload["file"]
                frappe.publish_realtime("data_import_error", {"data_import": 'Team Leader',"show_message": "missing employees", "file": missing_employee_file})
                return {"success": False, "message": "missing employees", "missing_employees_file": missing_employee_file}

            # TeamLeader exists in employee doctype conditon
            team_leaders_df = team_leaders_df[team_leaders_df["EID"].isin(
                get_employee_details)]

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

                file_upload = upload_file_api(
                    filename=team_leader_file_name)
                if not file_upload["success"]:
                    return file_upload

                dataimport(file=file_upload["file"], import_type="Insert New Records",
                            reference_doctype="Team Leaders")

            existing_team_leader_data = team_leaders_df[team_leaders_df["EID"].isin(
                team_leader_list)]
            if len(existing_team_leader_data) > 0:
                sort_existing_team_leaders = existing_team_leader_data.sort_values([
                    "Team Name"])
                sort_existing_team_leaders.rename(
                    columns={"MARSHA": "Marsha (Properties)", "Team Name": "Cluster"}, inplace=True)
                remove_duplicate_values = [
                    "Revenue Leader", "EID", "Email Id", "Cluster"]
                sort_existing_team_leaders[remove_duplicate_values] = sort_existing_team_leaders[remove_duplicate_values].where(
                    sort_existing_team_leaders[remove_duplicate_values].apply(lambda x: x != x.shift()), '')
                sort_existing_team_leaders.loc[sort_existing_team_leaders["Revenue Leader"].duplicated(
                ), "Revenue Leader"] = np.NaN

                sort_existing_team_leaders.to_csv(
                    team_leader_file_name, index=False)

                file_upload = upload_file_api(
                    filename=team_leader_file_name)
                if not file_upload["success"]:
                    return file_upload
                dataimport(file=file_upload["file"], import_type="Update Existing Records",
                            reference_doctype="Team Leaders")
            return {"success": True, "message": "Data Imported"}
        frappe.publish_realtime("data_import_error", {"data_import": 'Team Leader',"show_message": "Some columns are missing in excel file.", "file": ""})
        return {"success": False, "message": "Some columns are missing in excel file.", "missing_employees_file": ""}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("import_team_leader", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}



@frappe.whitelist()
def enque_team_leader_import(file=None):
    try:
        enqueue(
            import_team_leader,
            queue="long",
            timeout=800000,
            is_async=True,
            now=False,
            file=file,
            event="import_team_leader",
            job_name="Team_Leaders_Import"
        )
        return {"success": True, "Message": "Team Leaders Import Starts Soon"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("enque_team_leader_import", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}
