# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import os, sys
import requests
import traceback
import pandas as pd
from frappe.utils import cstr
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from revenue_management.utlis import dataimport, upload_file_api

class Employees(Document):
	pass


@frappe.whitelist()
def employees_import(file=None):
	try:
		if not file:
			frappe.publish_realtime("data_import_error", {"data_import": 'Employees',"show_message": "file is missing"})
			return {"success": False, "message": "file is missing"}
		site_name = cstr(frappe.local.site)
		file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + file
		excel_data_df = pd.read_excel(file_path)
		if len(excel_data_df) > 0:
			get_marsha_details = frappe.db.get_list('Marsha Details',  fields=["billing_unit", "marsha as Marsha"])
			if len(get_marsha_details) == 0:
				frappe.publish_realtime("data_import_error", {"data_import": 'Employees',"show_message": "no marsha details exists"})
				return {"success": False, "message": "no marsha details exists"}
			
			marsha_df = pd.DataFrame.from_records(get_marsha_details)
			billing_unit_list  = marsha_df['billing_unit'].tolist()

			missing_marsha = excel_data_df[~excel_data_df["Work Location Code"].isin(billing_unit_list)]

			if len(missing_marsha) > 0:
				missing_marsha_file = frappe.utils.get_bench_path() + "/sites/" + site_name + \
                        "/public/files/Missing Marshas.xlsx"
				missing_marsha.to_excel(missing_marsha_file, index=False)
				cluser_file_upload = upload_file_api(filename=missing_marsha_file)
				if not cluser_file_upload["success"]:
					return cluser_file_upload
				frappe.publish_realtime("data_import_error", {"data_import": 'Employees',"show_message": "missing billing unit in marsha details for some employees", "file": cluser_file_upload["file"]})
				return {"success": False, "message": "missing billing unit in marsha details for some employees", "file": cluser_file_upload["file"]}
			
			excel_data_df[['First Name', 'Last Name']] = excel_data_df["Person Name"].apply(lambda x: pd.Series(str(x).split(",")))

			excel_data_df.rename(columns={"Work Location Code": "billing_unit", "Person User Name": "EID"}, inplace=True)
			excel_data_df = pd.merge(excel_data_df, marsha_df, on="billing_unit")

			get_employee_list = frappe.db.get_list("Employees", pluck="name")
			excel_data_df.drop(['Person Name'], axis=1, inplace=True)
			excel_data_df.rename(columns={"billing_unit": "Billing Unit"})

			remove_existing_employee_list = excel_data_df[~excel_data_df["EID"].isin(get_employee_list)]
			employee_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
					"/public/files/Employees.csv"
			if len(remove_existing_employee_list) > 0:
				remove_existing_employee_list.to_csv(employee_file_name, sep=',', index=False)
				file_upload = upload_file_api(filename=employee_file_name)
				if not file_upload["success"]:
					return file_upload
				dataimport(file=file_upload["file"], import_type="Insert New Records",
							reference_doctype="Employees")

			existing_employee_list = excel_data_df[excel_data_df["EID"].isin(get_employee_list)]
			if len(existing_employee_list) > 0:
				existing_employee_list.rename(columns={"EID": "ID"}, inplace=True)
				existing_employee_list.to_csv(employee_file_name, sep=',', index=False)
				file_upload = upload_file_api(filename=employee_file_name)
				if not file_upload["success"]:
					return file_upload
				dataimport(file=file_upload["file"], import_type="Update Existing Records",
							reference_doctype="Employees")

			return {"success": True, "message": "Data Imported"}
		frappe.publish_realtime("data_import_error", {"data_import": 'Employees',"show_message": "file is empty"})
		return {"success": False, "message": "file is empty"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("employees_import", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "error": str(e)}



@frappe.whitelist()
def import_employees(file=None):
    try:
        enqueue(
            employees_import,
            queue="long",
            timeout=800000,
            is_async=True,
            now=False,
            file=file,
            event="import_employees",
            job_name="Employees_Import"
        )
        return {"success": True, "Message": "Employees Import Starts Soon"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("import_properties_team_leaders", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}
