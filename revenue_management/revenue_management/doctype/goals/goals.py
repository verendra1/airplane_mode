# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import datetime
import frappe
import sys, traceback
import pandas as pd
import numpy as np
from frappe.utils import cstr
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from revenue_management.utlis import get_current_quarter_months, dataimport, upload_file_api


class Goals(Document):
	pass


@frappe.whitelist()
def goal_maintance(goal_file, hotel_break_down_file):
	try:
		site_name = cstr(frappe.local.site)
		file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + goal_file
		hotel_break_down = frappe.utils.get_bench_path() + "/sites/" + site_name + hotel_break_down_file
		df = pd.read_excel(file_path)
		removed_unmaed_columns = df.loc[:, ~
										df.columns.str.contains('^Unnamed')]
		removed_duplicate_columns = removed_unmaed_columns.loc[:,
															   ~removed_unmaed_columns.columns.str.contains('.1')]
		categories = list(removed_duplicate_columns.columns)
		df.columns = df.iloc[0]
		df = df[1:]
		removed_totals = df.loc[:, ~df.columns.str.contains('^Quarter Total')]
		removed_totals.set_index('Marsha', inplace=True)
		final_data = []
		for each in categories[::-1]:
			col_index_map = {col_name: i for i,
							 col_name in enumerate(removed_totals.columns)}
			jan_index = col_index_map['Jan']
			split_df2 = removed_totals.iloc[:, jan_index:]
			removed_totals = removed_totals.iloc[:, :jan_index]
			converted_df = split_df2.apply(lambda x: x.apply(
				lambda y: {"month": x.name, "amount": y, "category": each}), axis=0)
			converted_df = converted_df.T
			# removed_totals.reset_index(inplace=True)
			# print(converted_df.to_string())
			data = converted_df.to_dict('list')
			for key, value in data.items():
				final_data.extend(
					list(map(lambda x: {**x, "marsha": key}, value)))

		
		hotel_bd_df = pd.read_excel(hotel_break_down)
		hotel_bd_df['Unnamed: 0'] = hotel_bd_df['Unnamed: 0'].replace(np.nan, "marsha")
		removed_unmaed_columns_of_hotel_db = hotel_bd_df.loc[:, ~
										hotel_bd_df.columns.str.contains('^Unnamed')]
		removed_duplicate_columns_hotel_db = removed_unmaed_columns_of_hotel_db.loc[:,
															   ~removed_unmaed_columns_of_hotel_db.columns.str.contains('.1')]
		dates = list(removed_duplicate_columns_hotel_db.columns)
		hotel_bd_df.columns = hotel_bd_df.iloc[0]
		hotel_bd_df = hotel_bd_df[1:]
		hotel_bd_df.set_index('marsha', inplace=True)
		avail_df = hotel_bd_df['Tymktavail']
		months = [datetime.datetime.strptime(value, '%B %Y').strftime('%b') for value in dates]
		avail_df = avail_df.set_axis(months, axis=1)
		converted_hotel_df = avail_df.apply(lambda x: x.apply(
				lambda y: {"month": x.name, "amount": y, "category": "Tymktavail"}), axis=0)
		converted_hotel_df = converted_hotel_df.T
		hotel_data = converted_hotel_df.to_dict('list')
		for key, value in hotel_data.items():
			final_data.extend(
				list(map(lambda x: {**x, "marsha": key}, value)))
		
		final_df = pd.DataFrame.from_records(final_data)
		final_df.replace(np.nan,0, inplace=True)
		final_df["Year"] = datetime.datetime.now().year
		final_df.rename(columns={'month': 'Month', 'marsha': 'Marsha', 'amount': "Amount", "category": "Category"}, inplace=True)
		goal_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
					"/public/files/Goals Details.csv"
		final_df.to_csv(
						goal_file_name, sep=',', index=False)
		file_upload = upload_file_api(filename=goal_file_name)
		if not file_upload["success"]:
			return file_upload
		frappe.db.delete("Goals", {"year": datetime.datetime.now().year})
		frappe.db.commit()
		# dataimport(file=file_upload["file"], import_type="Insert New Records",
		# 			reference_doctype="Goals")

		return {"success": True, "message": "file uploaded successfully"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("goal_maintance", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "error": str(e)}


@frappe.whitelist()
def import_goal_maintance(goal_file, hotel_break_down_file):
	try:
		enqueue(
			goal_maintance,  
			queue="short",
			timeout=800000,
			is_async=True,
			now=False,
			goal_file = goal_file,
			hotel_break_down_file = hotel_break_down_file,
			event="insert_d110_data",
			job_name="Goal_Maintance_D110_Import"
		)
		return {"success": True, "Message": "D110 Import Starts Soon"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("import_goal_maintance", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "error": str(e)}
	

@frappe.whitelist()
def get_goals(marsha=None, year=None):
	try:
		get_goals = frappe.db.get_list("Goals", filters={"marsha": marsha, "year": year}, fields=["category", "month", "amount"])
		if len(get_goals) == 0:
			return {"success": False, "message": "No data found"}
		df = pd.DataFrame.from_records(get_goals)
		group_df = df.groupby("category").agg({"amount": "sum"})
		group_df.replace(np.nan,0, inplace=True)
		sum_data = group_df.to_dict()
		piovt_df = pd.pivot_table(df, index= ['month'], columns = ['category'], values=['amount']).reset_index()
		# piovt_df.columns = piovt_df.iloc[0]
		piovt_df = piovt_df.droplevel(0, axis=1)
		piovt_df.rename(columns = {"" : "month", "Catering Rev":"Catering_Rev"}, inplace = True)
		piovt_df.replace(np.nan,0, inplace=True)
		data = piovt_df.to_dict('records')
		return {"success": False, "data": data, "totals": sum_data["amount"]}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("get_goals", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "error": str(e)}