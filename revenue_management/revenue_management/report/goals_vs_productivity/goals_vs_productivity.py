# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import sys, traceback
import pandas as pd
import numpy as np
from revenue_management.utlis import get_quarter_details
from revenue_management.revenue_management.doctype.calculations.quarter_calculations import quarter_rm_cat_rev_calculations, quarter_rpi_calculations_goals_vs_prod



def execute(filters=None):
	print(filters)
	columns, data = [], []
	goal_vs_productivity(filters)
	return columns, data


def goal_vs_productivity(filters):
	# try:
		get_quarter_months = get_quarter_details(filters["quarter"])
		if not get_quarter_months["success"]:
			return get_quarter_months
		filters["month"] = ["in", get_quarter_months["months"]]
		del filters["quarter"]
		get_goals = frappe.db.get_list("Goals", filters=filters, fields=["marsha", "category", "amount", "month"])
		get_productivity  = frappe.db.get_list("Productivity", filters=filters, fields=["marsha", "category", "amount as productivity_amount", "month"])
		if len(get_productivity) == 0 or len(get_goals) == 0:
			return []
		marsha_details = frappe.db.get_list("Marsha Details", fields=["marsha", "market_share_type", "ms_comp_non_comp"])
		marsha_df = pd.DataFrame.from_records(marsha_details)

		goals_df = pd.DataFrame.from_records(get_goals)
		# goals_df = goals_df.loc[(goals_df["category"].isin(["RPI", "RevPAR", "Catering Rev", "RmRev"]))]

		productivity_df = pd.DataFrame.from_records(get_productivity)
		# productivity_df = productivity_df.loc[(productivity_df["category"].isin(["RPI", "RevPAR", "Catering Rev", "RmRev"]))]

		
		quater_rm_cat_cal = quarter_rm_cat_rev_calculations(goals_df, productivity_df, rmip=False)
		if not quater_rm_cat_cal["success"]:
			return quater_rm_cat_cal
		
		goals_df_data = goals_df.loc[(goals_df["category"].isin(["Tymarravail", "Comp Set RevPAR Growth", "Tymktavail", "HBD RevPAR"]))]
		productivity_df_data = productivity_df.loc[(productivity_df["category"].isin(["Tymarravail", "Comp Set RevPAR Growth", "Tymktavail", "HBD RevPAR"]))]
		
		if len(goals_df_data) > 0 and len(productivity_df_data) > 0:
			goals_quater_rpi_cal = quarter_rpi_calculations_goals_vs_prod(goals_df, productivity_df)
			if not goals_quater_rpi_cal["success"]:
				return goals_quater_rpi_cal
			quater_rpi_rev = goals_quater_rpi_cal["df"]
		else:
			quater_rpi_rev = pd.DataFrame.from_records([{"category": "RPI", "goal": 0.0, "productivity": 0.0, "achieved": 0.0}])
		
		quater_rm_cat_rev = quater_rm_cat_cal["df"]
		quater_df = pd.concat([quater_rm_cat_rev, quater_rpi_rev], ignore_index=True, sort=False)
		quater_data = quater_df.to_dict("records")
		
		merge_goals = goals_df[["marsha", "category", "amount", 'month']]
		merge_goals = merge_goals.loc[(goals_df["category"].isin(["Catering Rev", "RmRev", "RPI"]))]
		pivot_goals = pd.pivot_table(merge_goals, index= ['marsha', "month"], columns = ['category'], values=['amount']).reset_index()
		pivot_goals_df = pivot_goals.droplevel(0, axis=1)
		pivot_goals_df.columns.values[0] = 'marsha'
		pivot_goals_df.columns.values[1] = 'month'
		# pivot_goals_df.rename(columns = {"" : "marsha"}, inplace = True)

		merge_productivity = productivity_df[["marsha", "category", "productivity_amount", "month"]]
		merge_productivity = merge_productivity.loc[(merge_productivity["category"].isin(["Catering Rev", "RmRev", "RPI"]))]
		pivot_productivity = pd.pivot_table(merge_productivity, index= ['marsha', 'month'], columns = ['category'], values=['productivity_amount']).reset_index()
		pivot_productivity_df = pivot_productivity.droplevel(0, axis=1)
		pivot_productivity_df.columns.values[0] = 'marsha'
		pivot_productivity_df.columns.values[1] = 'month'
		pivot_productivity_df.rename(columns = {"RPI": "productivity_RPI", "Catering Rev": "productivity_Catering_Rev", "RmRev": "productivity_RmRev"}, inplace = True)

		merge_both = pd.merge(pivot_goals_df, pivot_productivity_df, on=['month', 'marsha'], how="outer")
		merge_both.replace(np.nan,0, inplace=True)
		merge_both = merge_both.round(decimals = 2)
		merge_both["catering_rev_achieved"] = (merge_both["productivity_Catering_Rev"]/merge_both["Catering Rev"])*100
		merge_both["rmrev_achieved"] = (merge_both["productivity_RmRev"]/merge_both["RmRev"])*100
		# merge_both["revpar_weightage"] = (merge_both["productivity_RevPAR"]/merge_both["RevPAR"])*100
		merge_both["rpi_achieved"] = (merge_both["productivity_RPI"]/merge_both["RPI"])*100
		merge_both = merge_both.round(decimals = 2)
		merge_both.replace(np.nan,0, inplace=True)
		merge_both = merge_both[["month", "productivity_RmRev", "RmRev", "rmrev_achieved", "productivity_Catering_Rev","Catering Rev", "catering_rev_achieved", "productivity_RPI", "RPI", "rpi_achieved"]]
		merge_both.set_index('month', inplace=True)
		month_wise_date = merge_both.to_dict('index')
		
		return {"success": True, "quarter_wise_data": quater_data, "month_wise_data": month_wise_date}
	# except Exception as e:
	#     exc_type, exc_obj, exc_tb = sys.exc_info()
	#     frappe.log_error("goal_vs_productivity", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
	#     return {"success": False, "message": str(e)}