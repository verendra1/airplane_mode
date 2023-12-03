# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
import numpy as np
import sys, traceback
from frappe.utils import cstr
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from revenue_management.utlis import dataimport, upload_file_api
from revenue_management.revenue_management.doctype.goals.goals import extract_rpi_file


class Productivity(Document):
	pass


@frappe.whitelist()
def productivity_data_import(file=None, rpi_file=None, month=None, year=None):
	try:
		if not file and not rpi_file and not month and not year:
			return {"success": False, "message": "file or return_period is missing in filters"}
		get_marsha_details = frappe.db.get_all("Marsha Details",  fields=["name as marsha", "market_share_type", "ms_comp_non_comp", "team_type", "cluster"])
		if len(get_marsha_details) == 0:
			return {"success": False, "marsha": "Marsha details are empty"}
		marsha_df = pd.DataFrame.from_records(get_marsha_details)
		rpi_marshas = marsha_df.loc[(marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB')]
		rpi_marshas_list = rpi_marshas["marsha"].to_list()

		site_name = cstr(frappe.local.site)
		file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + file
		excel_data_df = pd.read_excel(file_path)
		if len(excel_data_df) == 0:
			return {"success": False, "message": "No data in the file"}
		empty_df = pd.DataFrame()
		productivity_df = excel_data_df[[
			"MARSHA_NEW", "Catering Rev.", "RevPAR", "Room Rev."]]
		productivity_df = productivity_df.loc[productivity_df['MARSHA_NEW'] != "Grand Total"]
		productivity_df.replace(np.nan, 0, inplace=True)
		setindex = productivity_df.set_index('MARSHA_NEW')
		for each in ["Catering Rev.", "RevPAR", "Room Rev."]:
			each_df= setindex[[each]]
			each_df.reset_index(inplace=True)
			each_df.rename(columns={each: "amount", "MARSHA_NEW": "marsha"}, inplace=True)
			each_df["category"] = each
			empty_df = pd.concat([empty_df, each_df], axis=0)
		empty_df.replace({"category": {"Catering Rev.": "Catering Rev", "RevPAR": "RevPAR", "Room Rev.": "RmRev"}}, inplace=True)
		empty_df["Month"] = month
		rpi_productivity_df = empty_df.loc[(empty_df["marsha"].isin(rpi_marshas_list)) & (empty_df["category"] != "RevPAR")]
		revpar_productivity_df = empty_df.loc[~(empty_df["marsha"].isin(rpi_marshas_list))]
		get_rpi_data = extract_rpi_file(filename=rpi_file, type="Productivity")
		if not get_rpi_data["success"]:
			return get_rpi_data
		hotel_df = pd.DataFrame.from_records(get_rpi_data["data"])
		final_df = pd.concat([rpi_productivity_df, revpar_productivity_df, hotel_df])
		final_df["Year"] = year
		productivity_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
			"/public/files/Productivity Details.csv"
		final_df.to_csv(
			productivity_file_name, sep=',', index=False)
		file_upload = upload_file_api(filename=productivity_file_name)
		if not file_upload["success"]:
			return file_upload
		frappe.db.delete("Productivity", {"year": year, "month": month})
		frappe.db.commit()
		dataimport(file=file_upload["file"], import_type="Insert New Records",
				reference_doctype="Productivity")
		return {"success": True, "message": "file uploaded successfully"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("import_properties_team_leaders", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def import_productivity(file=None, rpi_file=None, month=None, year=None):
	try:
		enqueue(
			productivity_data_import,  
			queue="short",
			timeout=800000,
			is_async=True,
			now=False,
			file = file,
			rpi_file = rpi_file,
			month = month,
			year = year,
			event="insert_productivity_data",
			job_name="Productivity_Maintance_Import"
		)
		return {"success": True, "Message": "Goals Import Starts Soon"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("import_productivity", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_productivity(month=None, year=None):
	try:
		get_productivity = frappe.db.get_list("Productivity", filters={"year": year, "month": month, "category": ["in", ["Catering Rev", "RPI", "RevPAR", "RmRev"]]}, fields=["category", "month", "amount", "marsha"])
		if len(get_productivity) == 0:
			return {"success": False, "message": "productivity details not found"}
		empty_dataframe = pd.DataFrame(columns=["month", "Catering_Rev", "RPI", "RevPAR", "RmRev"])
		df = pd.DataFrame.from_records(get_productivity)
		piovt_df = pd.pivot_table(df, index= ['marsha'], columns = ['category'], values=['amount']).reset_index()
		piovt_df = piovt_df.droplevel(0, axis=1)
		piovt_df.rename(columns = {"" : "marsha", "Catering Rev":"Catering_Rev"}, inplace = True)
		final_df = pd.concat([empty_dataframe, piovt_df])
		final_df.replace(np.nan,0, inplace=True)
		data = final_df.to_dict('records')
		return {"success": True, "data": data}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("get_productivity", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}