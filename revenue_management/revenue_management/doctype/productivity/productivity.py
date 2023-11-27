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
def import_productivity(file=None, rpi_file=None, month=None, year=None):
	try:
		if not file and not rpi_file and not month and not year:
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
		empty_df.replace({"category": {"Catering Rev.": "Catering Rev", "RevPAR": "RevPAR", "Room Rev.": "RmRev"}}, inplace=True)

		get_rpi_data = extract_rpi_file(filename=rpi_file)
		if not get_rpi_data["success"]:
			return get_rpi_data
		hotel_df = pd.DataFrame.from_records(get_rpi_data["data"])
		hotel_df = hotel_df[hotel_df["category"] == "RPI"]
		empty_df["Month"] = month
		final_df = pd.concat([empty_df, hotel_df])
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
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_productivity(month=None, year=None):
	try:
		get_marsha_details =  frappe.db.get_list("Marsha Details", fields=["marsha", "market_share_type", "ms_comp_non_comp"])
		get_productivity = frappe.db.get_list("Productivity", filters={"year": year, "month": month}, fields=["category", "month", "amount", "marsha"])
		if len(get_marsha_details) == 0:
			return {"success": False, "message": "marsha details not found"}
		if len(get_productivity) == 0:
			return {"success": False, "message": "productivity details not found"}
		empty_dataframe = pd.DataFrame(columns=["month", "Catering_Rev", "RPI", "RevPAR", "RmRev"])
		marsha_df = pd.DataFrame.from_records(get_marsha_details)
		df = pd.DataFrame.from_records(get_productivity)
		piovt_df = pd.pivot_table(df, index= ['marsha'], columns = ['category'], values=['amount']).reset_index()
		piovt_df = piovt_df.droplevel(0, axis=1)
		piovt_df.rename(columns = {"" : "marsha", "Catering Rev":"Catering_Rev"}, inplace = True)
		merge_df = pd.merge(piovt_df, marsha_df, on=["marsha"])
		rpi = merge_df.loc[(merge_df['ms_comp_non_comp'] == 'Y') & (merge_df['market_share_type'] == 'SB')]
		rpi_df = rpi[["marsha", "Catering_Rev", "RmRev", "RPI"]]
		revpar = merge_df.loc[(merge_df['ms_comp_non_comp'] != 'Y') & (merge_df['market_share_type'] != 'SB')]
		revpar_df = revpar[["marsha", "Catering_Rev", "RmRev", "RevPAR"]]
		final_df = pd.concat([empty_dataframe, rpi_df, revpar_df])
		final_df.replace(np.nan,0, inplace=True)
		data = final_df.to_dict('records')
		return {"success": True, "data": data}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("get_productivity", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "error": str(e)}