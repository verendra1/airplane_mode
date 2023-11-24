# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import pandas as pd
import numpy as np
import sys, traceback
from frappe.utils import cstr
from frappe.model.document import Document
from revenue_management.utlis import dataimport, upload_file_api
from revenue_management.revenue_management.doctype.goals.goals import extract_rpi_file


class Productivity(Document):
	pass


@frappe.whitelist()
def import_productivity(file=None, rpi_file=None, return_period=None):
	try:
		if not file and not return_period:
			return {"success": False, "message": "file or return_period is missing in filters"}
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
		year = return_period[2:]
		month = return_period[:2]
		months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
				  "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"}
		month = months[month]
		empty_df.replace({"category": {"Catering Rev.": "Catering Rev", "RevPAR": "RevPAR", "Room Rev.": "RmRev"}}, inplace=True)

		get_rpi_data = extract_rpi_file(filename=rpi_file)
		if not get_rpi_data["success"]:
			return get_rpi_data
		hotel_df = pd.DataFrame.from_records(get_rpi_data["data"])
		hotel_df = hotel_df[hotel_df["category"] == "RPI"]
		final_df = pd.concat([empty_df, hotel_df])
		final_df["Year"] = year
		final_df["Month"] = month
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
		return {"success": False, "error": str(e)}
