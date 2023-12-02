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
def old_goal_maintance(goal_file, hotel_break_down_file):
	try:
		site_name = cstr(frappe.local.site)
		file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + goal_file
		hotel_break_down = frappe.utils.get_bench_path() + "/sites/" + site_name + hotel_break_down_file

		get_marsha_details = frappe.db.get_all("Marsha Details",  fields=["name as marsha", "market_share_type", "ms_comp_non_comp", "team_type", "cluster"])
		if len(get_marsha_details) == 0:
			return {"success": False, "marsha": "Marsha details are empty"}
		marsha_df = pd.DataFrame.from_records(get_marsha_details)

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
		goals_data = []
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
				goals_data.extend(
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
		avail_df = hotel_bd_df[['Tymktavail','RevPAR', 'Comp Set RevPAR', 'Tymarravail', 'RPI']]
		hotel_db_data = []
		for each in ['Tymktavail','RevPAR', 'Comp Set RevPAR', 'Tymarravail', 'RPI']:
			each_df = avail_df[each]
			months = [datetime.datetime.strptime(value, '%B %Y').strftime('%b') for value in dates]
			each_df = each_df.set_axis(months, axis=1)
			converted_hotel_df = each_df.apply(lambda x: x.apply(
					lambda y: {"month": x.name, "amount": y, "category": each}), axis=0)
			converted_hotel_df = converted_hotel_df.T
			hotel_data = converted_hotel_df.to_dict('list')
			for key, value in hotel_data.items():
				hotel_db_data.extend(
					list(map(lambda x: {**x, "marsha": key}, value)))
				

		get_non_cluster_rev_par_marshas = marsha_df.loc[(marsha_df['ms_comp_non_comp'] != 'Y') & (marsha_df['market_share_type'] != 'SB') & (marsha_df['team_type'] == 'Non-Cluster')]
		non_cluster_rev_par_marshas_list = get_non_cluster_rev_par_marshas["marsha"].to_list()

		get_non_cluster_rpi_marshas = marsha_df.loc[(marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB') & (marsha_df['team_type'] == 'Non-Cluster')]
		non_cluster_rpi_marshas_list = get_non_cluster_rpi_marshas["marsha"].to_list()

		get_cluster_rpi_marshas = marsha_df.loc[(marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB') & (marsha_df['team_type'] == 'Cluster')]
		cluster_rpi_marshas_list = get_cluster_rpi_marshas["marsha"].to_list()

		goal_df = pd.DataFrame.from_records(goals_data)
		goals_for_non_cluster_rev_par = goal_df.loc[(goal_df['marsha'].isin(non_cluster_rev_par_marshas_list))]


		goals_for_non_cluster_rpi = goal_df.loc[(goal_df['marsha'].isin(non_cluster_rpi_marshas_list))]
		remove_rev_par_for_rpi = goals_for_non_cluster_rpi[goals_for_non_cluster_rpi["category"] != "RevPAR"]

		hotel_db_final_data = pd.DataFrame.from_records(hotel_db_data)

		rpi_data_from_hotel_db = hotel_db_final_data[hotel_db_final_data["category"] == "RPI"]
		rpi_data_for_non_cluster = rpi_data_from_hotel_db.loc[(rpi_data_from_hotel_db['marsha'].isin(non_cluster_rpi_marshas_list))]

		calculate_rpi_data_for_cluster = hotel_db_final_data.loc[(hotel_db_final_data['marsha'].isin(cluster_rpi_marshas_list))]
		calculate_rpi_data_for_cluster = calculate_rpi_data_for_cluster[calculate_rpi_data_for_cluster["category"] != "RPI"]
		piovt_cluster_rpi_data = pd.pivot_table(calculate_rpi_data_for_cluster, values ='amount', index =['marsha', 'month'], columns =['category']).reset_index()
		piovt_cluster_rpi_data["rev"] = (piovt_cluster_rpi_data["RevPAR"] * piovt_cluster_rpi_data["Tymarravail"])/piovt_cluster_rpi_data["Tymarravail"]
		piovt_cluster_rpi_data["cs_rev"] = (piovt_cluster_rpi_data["Comp Set RevPAR"] * piovt_cluster_rpi_data["Tymktavail"])/piovt_cluster_rpi_data["Tymktavail"]
		piovt_cluster_rpi_data["RPI"] = (piovt_cluster_rpi_data["rev"] / piovt_cluster_rpi_data["cs_rev"])*100
		rpi_data_for_cluster = piovt_cluster_rpi_data[["marsha", "month", "RPI"]]
		rpi_data_for_cluster["category"] = "RPI"
		rpi_data_for_cluster.rename(columns={'RPI': 'amount'}, inplace=True)

		
		
		# piovt_df.rename(columns = {"" : "month"}, inplace = True)
		# print(piovt_df.to_string())
		



		# get_rpi_marsha_codes_for_non_cluster = marsha_df.loc[(marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB') & (marsha_df['team_type'] == 'Non-Cluster')]
		# rpi_marsha_codes_for_non_cluster = get_rpi_marsha_codes_for_non_cluster['marsha'].tolist()
		# get_non_rpi_marsha_codes_for_non_cluster = marsha_df.loc[(marsha_df['ms_comp_non_comp'] != 'Y') & (marsha_df['market_share_type'] != 'SB') & (marsha_df['team_type'] == 'Non-Cluster')]
		# non_rpi_marsha_codes_for_non_cluster = get_non_rpi_marsha_codes_for_non_cluster["marsha"].tolist()

		# get_non_rpi_marsha_codes_for_cluster = marsha_df.loc[(marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB') & (marsha_df['team_type'] == 'Cluster')]
		# non_rpi_marsha_codes_for_cluster = get_non_rpi_marsha_codes_for_cluster["marsha"].tolist()


		# goal_df = pd.DataFrame.from_records(goals_data)
		# merge_goal_df_with_rpi = marsha_df.merge(goal_df, on=['marsha'], how='left', indicator=True)
		# both_merge_df = merge_goal_df_with_rpi[merge_goal_df_with_rpi['_merge'] == "both"]
		# goals_non_cluster_data = both_merge_df[both_merge_df["team_type"] == "Non-Cluster"]
		# filter_rpi_data_for_non_cluster = goals_non_cluster_data.loc[(goals_non_cluster_data['marsha'].isin(rpi_marsha_codes_for_non_cluster)) & (goals_non_cluster_data['category'] != "RevPAR")]
		# filter_rpi_data_for_non_cluster = filter_rpi_data_for_non_cluster[["marsha", "month", "amount", "category"]]

		# filter_non_rpi_data_for_non_cluster = goals_non_cluster_data.loc[(goals_non_cluster_data['marsha'].isin(non_rpi_marsha_codes_for_non_cluster))]
		# filter_non_rpi_data_for_non_cluster = filter_non_rpi_data_for_non_cluster[["marsha", "month", "amount", "category"]]
		

		goals_cluster_data = marsha_df[marsha_df["team_type"] == "Cluster"]
		check_market_share_type_unique = goals_cluster_data.groupby('cluster').market_share_type.nunique() > 1
		check_ms_comp_unique = goals_cluster_data.groupby('cluster').ms_comp_non_comp.nunique() > 1
		merge_market_share_type_with_ms_comp = pd.merge(check_market_share_type_unique, check_ms_comp_unique, on='cluster')
		get_same_market_share_and_ms_comp = merge_market_share_type_with_ms_comp.loc[(merge_market_share_type_with_ms_comp['market_share_type'] == False) & (merge_market_share_type_with_ms_comp['ms_comp_non_comp'] == False)]
		clusters_of_same_market_share_and_ms_comp = get_same_market_share_and_ms_comp.index.to_list()

		get_diff_market_share_and_ms_comp = merge_market_share_type_with_ms_comp.loc[(merge_market_share_type_with_ms_comp['market_share_type'] != False) & (merge_market_share_type_with_ms_comp['ms_comp_non_comp'] != False)]
		clusters_of_diff_market_share_and_ms_comp = get_diff_market_share_and_ms_comp.index.to_list()


		get_rev_par_cluster_unique_values  = marsha_df.loc[(marsha_df['cluster'].isin(clusters_of_same_market_share_and_ms_comp)) & (marsha_df['ms_comp_non_comp'] != 'Y') & (marsha_df['market_share_type'] != 'SB')]
		unique_rev_par_marsha_details_list = get_rev_par_cluster_unique_values["marsha"].to_list()
	
		get_unique_cluster_goals_revpar_data = goal_df.loc[goal_df["marsha"].isin(unique_rev_par_marsha_details_list)]


		get_rpi_cluster_unique_values  = marsha_df.loc[(marsha_df['cluster'].isin(clusters_of_same_market_share_and_ms_comp)) & (marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB')]
		unique_rpi_marsha_details_list = get_rpi_cluster_unique_values["marsha"].to_list()

		get_unique_cluster_goals_rpi_data = goal_df.loc[goal_df["marsha"].isin(unique_rpi_marsha_details_list) & (goal_df["category"] != 'RevPAR')]

		get_unique_cluster_hbd_rpi_data = rpi_data_for_cluster.loc[(rpi_data_for_cluster["marsha"].isin(unique_rpi_marsha_details_list))]

		# get_diff_market_share_and_ms_comp_marsha_details = marsha_df.loc[(marsha_df['cluster'].isin(clusters_of_diff_market_share_and_ms_comp))]
		# get_diff_marsha_list = get_diff_market_share_and_ms_comp_marsha_details.to_dict('records')
		# for each in get_diff_marsha_list:
			
		for each in clusters_of_diff_market_share_and_ms_comp:
			cluster_goal_details_based_on_cluster_revpar = marsha_df.loc[(marsha_df["cluster"] == each) & (marsha_df['ms_comp_non_comp'] != 'Y') & (marsha_df['market_share_type'] != 'SB')]
			goal_details_revpar = goal_df.loc[(goal_df["marsha"].isin(cluster_goal_details_based_on_cluster_revpar["marsha"].to_list()))]

			cluster_goal_details_based_on_cluster_rpi = marsha_df.loc[(marsha_df["cluster"] == each) & (marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB')]
			goal_details_rpi = goal_df.loc[(goal_df["marsha"].isin(cluster_goal_details_based_on_cluster_rpi["marsha"].to_list())) & (goal_df["category"] != 'RevPAR')]

			hdb_rpi_cluster = rpi_data_from_hotel_db.loc[(rpi_data_from_hotel_db['marsha'].isin(cluster_goal_details_based_on_cluster_rpi["marsha"].to_list()))]

			merge_cluster_data = pd.concat([goal_details_revpar, goal_details_rpi, hdb_rpi_cluster])
			merge_cluster_details = pd.pivot_table(merge_cluster_data, values ='amount', index =['marsha', 'month'], columns =['category']).reset_index()
			merge_cluster_details.replace(np.nan,0, inplace=True)
			group_data_by_month = merge_cluster_details.groupby("month").agg({"RmRev": "sum"})
			group_data_by_month.rename(columns={"RmRev": "SumRmRev"}, inplace=True)
			group_data_by_month.reset_index(inplace=True)
			merge_group_data_with_above_df = pd.merge(merge_cluster_details, group_data_by_month, on='month')
			merge_group_data_with_above_df["weightage"] = (merge_group_data_with_above_df["RmRev"]/ merge_group_data_with_above_df["SumRmRev"])*100
			print(merge_group_data_with_above_df.to_string())
			break






		



		
		

		
		months = [datetime.datetime.strptime(value, '%B %Y').strftime('%b') for value in dates]
		# avail_df = avail_df.set_axis(months, axis=1)
		# converted_hotel_df = avail_df.apply(lambda x: x.apply(
		# 		lambda y: {"month": x.name, "amount": y, "category": "RPI"}), axis=0)
		# converted_hotel_df = converted_hotel_df.T
		# hotel_data = converted_hotel_df.to_dict('list')
		# for key, value in hotel_data.items():
		# 	final_data.extend(
		# 		list(map(lambda x: {**x, "marsha": key}, value)))
		
		# final_df = pd.DataFrame.from_records(final_data)
		# final_df.replace(np.nan,0, inplace=True)
		# final_df["Year"] = datetime.datetime.now().year
		# final_df.rename(columns={'month': 'Month', 'marsha': 'Marsha', 'amount': "Amount", "category": "Category"}, inplace=True)
		# goal_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
		# 			"/public/files/Goals Details.csv"
		# final_df.to_csv(
		# 				goal_file_name, sep=',', index=False)
		# file_upload = upload_file_api(filename=goal_file_name)
		# if not file_upload["success"]:
		# 	return file_upload
		# frappe.db.delete("Goals", {"year": datetime.datetime.now().year})
		# frappe.db.commit()
		# dataimport(file=file_upload["file"], import_type="Insert New Records",
		# 			reference_doctype="Goals")

		return {"success": True, "message": "file uploaded successfully"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("goal_maintance", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}
	

def goal_maintance(goal_file, hotel_break_down_file):
	try:
		site_name = cstr(frappe.local.site)
		file_path = frappe.utils.get_bench_path() + "/sites/" + site_name + goal_file

		get_marsha_details = frappe.db.get_all("Marsha Details",  fields=["name as marsha", "market_share_type", "ms_comp_non_comp", "team_type", "cluster"])
		if len(get_marsha_details) == 0:
			return {"success": False, "marsha": "Marsha details are empty"}
		marsha_df = pd.DataFrame.from_records(get_marsha_details)
		rpi_marshas = marsha_df.loc[(marsha_df['ms_comp_non_comp'] == 'Y') & (marsha_df['market_share_type'] == 'SB')]
		rpi_marshas_list = rpi_marshas["marsha"].to_list()

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
		goals_data = []
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
				goals_data.extend(
					list(map(lambda x: {**x, "marsha": key}, value)))
		goals_df = pd.DataFrame.from_records(goals_data)
		rpi_goals_df = goals_df.loc[(goals_df["marsha"].isin(rpi_marshas_list)) & (goals_df["category"] != "RevPAR")]
		revpar_goals_df = goals_df.loc[~(goals_df["marsha"].isin(rpi_marshas_list))]
		get_rpi_data = extract_rpi_file(filename=hotel_break_down_file)
		if not get_rpi_data["success"]:
			return get_rpi_data
		hotel_df = pd.DataFrame.from_records(get_rpi_data["data"])
		final_df = pd.concat([rpi_goals_df, revpar_goals_df, hotel_df])
		final_df["Year"] = datetime.datetime.now().year
		final_df["amount"].replace(np.nan,0, inplace=True)
		goal_file_name = frappe.utils.get_bench_path() + "/sites/" + site_name + \
					"/public/files/Goals Details.csv"
		final_df.to_csv(
						goal_file_name, sep=',', index=False)
		file_upload = upload_file_api(filename=goal_file_name)
		if not file_upload["success"]:
			return file_upload
		frappe.db.delete("Goals", {"year": datetime.datetime.now().year})
		frappe.db.commit()
		dataimport(file=file_upload["file"], import_type="Insert New Records",
					reference_doctype="Goals")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("goal_maintance", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


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
			event="insert_goals_data",
			job_name="Goal_Maintance_Import"
		)
		return {"success": True, "Message": "Goals Import Starts Soon"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("import_goal_maintance", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}
	

@frappe.whitelist()
def get_goals(marsha=None, year=None):
	try:
		get_goals = frappe.db.get_list("Goals", filters={"marsha": marsha, "year": year, "category": ["in", ["Catering Rev", "RPI", "RevPAR", "RmRev"]]}, fields=["category", "month", "amount"])
		if len(get_goals) == 0:
			return {"success": False, "message": "No data found"}
		empty_dataframe = pd.DataFrame(columns=["month", "Catering_Rev", "RPI", "RevPAR", "RmRev"])
		df = pd.DataFrame.from_records(get_goals)
		group_df = df.groupby("category").agg({"amount": "sum"})
		group_df.replace(np.nan,0, inplace=True)
		sum_data = group_df.to_dict()
		remaining_sum_data = {each:0 for each in ["Catering Rev", "RPI", "RevPAR", "RmRev"] if each not in sum_data["amount"]}
		sum_data = sum_data["amount"] | remaining_sum_data
		piovt_df = pd.pivot_table(df, index= ['month'], columns = ['category'], values=['amount']).reset_index()
		# piovt_df.columns = piovt_df.iloc[0]
		piovt_df = piovt_df.droplevel(0, axis=1)
		piovt_df.rename(columns = {"" : "month", "Catering Rev":"Catering_Rev"}, inplace = True)
		final_df = pd.concat([empty_dataframe, piovt_df])
		final_df.replace(np.nan,0, inplace=True)
		months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
		final_df['month'] = pd.Categorical(final_df['month'], categories=months, ordered=True)
		final_df = final_df.sort_values(by="month")
		data = final_df.to_dict('records')
		return {"success": True, "data": data, "totals": sum_data}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("get_goals", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def get_goals_for_update(month=None, year=None, marsha=None):
	try:
		if not month and not year and not marsha:
			return {'success': False, "messsage": 'month or year or marsha is missing in filters'}
		data = frappe.db.get_list("Goals", filters={"month": month, "year": year, "marsha": marsha}, fields=["name", "category", "amount"])
		if len(data) > 0:
			df = pd.DataFrame.from_records(data)
			df.replace("Catering Rev", "Catering_Rev", inplace=True)
			df_data = df.to_dict('records')
			return {"success": True, "data": df_data}
		return {"success": False, "message": "No data found"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("get_goals_for_update", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}
	

@frappe.whitelist()
def update_goals(data=[], month=None, year=None, marsha=None):
	try:
		if len(data) == 0:
			return {"success": False, "message": "No data found to update"}
		for each in data:
			frappe.db.set_value("Goals", each["name"], {"amount": each["amount"], "reason": each["reason"] if "reason" in each else None}, update_modified=True)
			frappe.db.commit()
		return {"success": True, "message": "goals updated"}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("update_goals", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


def extract_rpi_file(filename=None):
	try:
		get_rpi_marshas = frappe.db.get_list("Marsha Details", filters={"market_share_type": "Y", "market_share_type": "SB"}, pluck="name")
		site_name = cstr(frappe.local.site)
		hotel_break_down = frappe.utils.get_bench_path() + "/sites/" + site_name + filename
		hotel_bd_df = pd.read_excel(hotel_break_down)
		removed_unmaed_columns_of_hotel_db = hotel_bd_df.loc[:, ~
										hotel_bd_df.columns.str.contains('^Unnamed')]
		# # removed_duplicate_columns_hotel_db = removed_unmaed_columns_of_hotel_db.loc[:,
		# # 													   ~removed_unmaed_columns_of_hotel_db.columns.str.contains('.1')]
		dates = list(removed_unmaed_columns_of_hotel_db.columns)
		columns = hotel_bd_df.columns.to_list()
		if len(dates) > 0:
			if dates[-1].isnumeric():
				ind = columns.index(dates[-1])
				main_columns = columns[:ind]
				hotel_bd_df = hotel_bd_df[main_columns]
				del dates[-1]
		hotel_bd_df.columns = hotel_bd_df.iloc[0]
		hotel_bd_df = hotel_bd_df[1:]
		remove_grand_total = hotel_bd_df[hotel_bd_df["Marsha Code"] != "Grand Total"]
		only_rpi_marsha_data = remove_grand_total.loc[remove_grand_total["Marsha Code"].isin(get_rpi_marshas)]
		only_rpi_marsha_data.set_index('Marsha Code', inplace=True)
		avail_df = only_rpi_marsha_data[['Tymktavail','RevPAR', 'Comp Set RevPAR', 'Tymarravail', 'RPI']]
		avail_df.rename(columns={'RevPAR': 'HBD RevPAR'}, inplace=True)
		avail_df["RPI"] = (avail_df["RPI"]*100)+2
		hotel_db_data = []
		for each in ['Tymktavail','HBD RevPAR', 'Comp Set RevPAR', 'Tymarravail', 'RPI']:
			each_df = avail_df[each]
			months = [datetime.datetime.strptime(value, '%B %Y').strftime('%b') for value in dates]
			each_df = each_df.set_axis(months, axis=1)
			converted_hotel_df = each_df.apply(lambda x: x.apply(
					lambda y: {"month": x.name, "amount": y, "category": each}), axis=0)
			converted_hotel_df = converted_hotel_df.T
			hotel_data = converted_hotel_df.to_dict('list')
			for key, value in hotel_data.items():
				hotel_db_data.extend(
					list(map(lambda x: {**x, "marsha": key}, value)))
		if len(hotel_db_data) > 0:
			return {"success": True, "data": hotel_db_data}
		return {"success": False, "message": "no data found in Hbreakdown file."}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("extract_rpi_file", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}
