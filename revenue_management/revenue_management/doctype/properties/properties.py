# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import datetime
import frappe
import json
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
			return {"success": False, "message": "The file was not provided."}
		site_name = cstr(frappe.local.site)
		file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + file
		excel_data_df = pd.read_excel(file_path)
		if len(excel_data_df) == 0:
			frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "No data discovered in the Properties file.", "user": frappe.session.user})
			return {"success": False, "message": "No data discovered in the Properties file."}
		masha_details_columns = ["MARSHA", "Property Name on Tableau", "Status", "Area", "ADRS", "City",
								 "Team Name", "Currency", "Country", "Market Share Type", "Market Share Comp", "Team Type", "Billing Unit"]
		if set(masha_details_columns).issubset(excel_data_df.columns):
			cluster_details = get_cluster_details()
			if not cluster_details["success"]:
				frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": cluster_details["message"], "user": frappe.session.user})
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
					frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "Cluster details are absent for certain properties.", "file": cluser_file_upload["file"], "user": frappe.session.user})
					return {"success": False, "message": "Cluster details are absent for certain properties.", "file": cluser_file_upload["file"]}
				status = ["Open", "Cancelled", "Not Yet Opened", "Deflagged"]
				get_records_except_above_status = masha_details_df[~masha_details_df["Status"].isin(status)]
				if len(get_records_except_above_status) > 0:
					extra_status_file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + "/public/files/Wrong Marsha Status.xlsx"
					get_records_except_above_status.to_excel(extra_status_file_path, index=False)
					status_file_upload = upload_file_api(
						filename=extra_status_file_path)
					if not status_file_upload["success"]:
						return status_file_upload
					frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "Additional statuses apart from Open, Cancelled, Not Yet Opened, and Deflagged.", "file": status_file_upload["file"], "user": frappe.session.user})
					return {"success": False, "message": "Additional statuses apart from Open, Cancelled, Not Yet Opened, and Deflagged.", "file": status_file_upload["file"]}
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
				return {"success": True, "message": "The file has been successfully uploaded."}
			frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "Unable to locate Property Details.", "user": frappe.session.user})
			return {"success": False, "message": "Unable to locate Property Details."}
		frappe.publish_realtime("data_import_error", {"data_import": 'Marsha Details',"show_message": "Certain columns are absent in the Excel file.", "user": frappe.session.user})
		return {"success": False, "message": "Certain columns are absent in the Excel file."}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("import_properties", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


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
		return {"success": True, "Message": "Properties Import Initiates Shortly."}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("import_properties_team_leaders", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def verify_excel_headers(columns=[], sub_columns=[], type=None):
	try:
		if len(columns) == 0:
			return {"success": False, "message": "The columns are devoid of content."}
		if isinstance(columns, str):
			columns = json.loads(columns)
		if isinstance(sub_columns, str):
			sub_columns = json.loads(sub_columns)
		if type == "Properties":
			masha_details_columns = ["MARSHA", "Property Name on Tableau", "Status", "Area", "ADRS", "City",
									"Team Name", "Currency", "Country", "Market Share Type", "Market Share Comp", "Team Type", "Billing Unit"]
			if set(masha_details_columns).issubset(columns):
				return {"success": True, "message": "Columns have been successfully matched."}
			return {"success": False, "message": "There is a mismatch in the columns."}
		elif type == "Employees":
			emplyee_columns = ["Person User Name", "Person Name", "Job Name", "Career Band", "Work Location Code", "Work Email Address", "Job Entry Date"]
			if set(emplyee_columns).issubset(columns):
				return {"success": True, "message": "Columns have been successfully matched."}
			return {"success": False, "message": "There is a mismatch in the columns."}
		elif type == "Team Leader":
			team_leader_columns = ["Revenue Leader", "EID", "Email Id", "Team Name", "MARSHA"]
			if set(team_leader_columns).issubset(columns):
				return {"success": True, "message": "Columns have been successfully matched."}
			return {"success": False, "message": "There is a mismatch in the columns."}
		elif type == "Goal":
			goals_columns = ["RevPAR", "Catering Rev", "RmRev", "AVAILRMS_TY"]
			goals_sub_columns = ["Marsha","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Quarter Total"]
			if set(goals_columns).issubset(columns) and set(sub_columns).issubset(goals_sub_columns):
				return {"success": True, "message": "Columns have been successfully matched."}
			return {"success": False, "message": "There is a mismatch in the columns."}
		elif type == "GoalHBreakDown":
			if columns[-1].isnumeric():
				del columns[-1]
			months = [datetime.datetime.strptime(value, '%B %Y').strftime('%b') for value in columns]
			hdb_columns = ['Marsha Code', 'RevPAR Rank', 'Occ.', 'Comp Set Occ.', 'ADR', 'Comp Set ADR', 'RevPAR', 'Comp Set RevPAR', 'RPI', 'RPI % Point Change', 'Tymarravail', 'Tymktavail']
			if len(months)>0 and set(sub_columns).issubset(hdb_columns):
				return {"success": True, "message": "Columns have been successfully matched."}
			return {"success": False, "message": "There is a mismatch in the columns."}
		elif type == "Productivity":
			goals_columns = ['MARSHA_NEW', 'Gross Op. Rev. (GOR)', 'GOR % Chg', 'Room Rev. $ Chg', 'Occ. Rate Pt. Chg', 'ADR % Chg', 'RevPAR % Chg', 'F&B Rev. % Chg', 'Rest./Lounges & IRD Rev. % Chg', 
					'Catering Rev. % Chg', 'Prop Count', 'ADR', 'Top - ADR - DS vs. CT ($)', 'Rest./Lounges Rev.', 'Top - BarRest Conv - DS vs. CT ($)', 'Catering Rev.', 'Top - CtRev Conv - DS vs. CT ($)', 
					'F&B Rev.', 'Top - FBRev Conv - DS vs. CT ($)', 'Top - GOR Conv - DS vs. CT ($)', 'Occ. Rate', 'RevPAR', 'Top - RevPAR - DS vs. CT ($)', 'Room Rev.']
			if set(goals_columns).issubset(columns):
				return {"success": True, "message": "Columns have been successfully matched."}
			return {"success": False, "message": "There is a mismatch in the columns."}
		elif type == "RPI File":
			months = [datetime.datetime.strptime(value, '%B %Y').strftime('%b') for value in columns]
			hdb_columns = ['Marsha Code', 'RevPAR Rank', 'Occ.', 'Comp Set Occ.', 'ADR', 'Comp Set ADR', 'RevPAR', 'Comp Set RevPAR', 'RPI', 'RPI % Point Change', 'Tymarravail', 'Tymktavail']
			if len(months)>0 and set(sub_columns).issubset(hdb_columns):
				return {"success": True, "message": "Columns have been successfully matched."}
			return {"success": False, "message": "There is a mismatch in the columns."}
		else:
			return {"success": False, "message": "The provided file name does not match."}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("verify_properties_columns", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}
