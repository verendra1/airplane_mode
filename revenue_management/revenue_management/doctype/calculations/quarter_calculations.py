import frappe
import sys, traceback
import pandas as pd
import numpy as np

def quarter_rpi_calculations(df):
	try:
		piovt_rpi = pd.pivot_table(df, values ='amount', index =['marsha', 'month'], columns =['category']).reset_index()
		piovt_rpi.replace(np.nan,0, inplace=True)
		piovt_rpi["rev"] = piovt_rpi["HBD RevPAR"] * piovt_rpi["Tymarravail"]
		piovt_rpi["cs_rev"] = piovt_rpi["Comp Set RevPAR"] * piovt_rpi["Tymktavail"]
		group_rpi = piovt_rpi.groupby(["marsha"]).agg({"Tymarravail": "sum", "Tymktavail": "sum", "rev": "sum", "cs_rev": "sum"}).reset_index()
		group_rpi["quater_revpar"] = group_rpi["rev"]/group_rpi["Tymarravail"]
		group_rpi["quater_cs_revpar"] = group_rpi["cs_rev"]/group_rpi["Tymktavail"]
		group_rpi["quarter_rpi"] = (group_rpi["quater_revpar"]/group_rpi["quater_cs_revpar"])*100
		return {"success": True, "df": group_rpi[["marsha", "quarter_rpi"]]}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("quarter_rpi_calculations", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


def quarter_rpi_calculations_goals_vs_prod(goals_df, productivity_df):
	try:
		goals_df_data = goals_df.loc[(goals_df["category"].isin(["Tymarravail", "Comp Set RevPAR", "Tymktavail", "HBD RevPAR"]))]
		productivity_df_data = productivity_df.loc[(productivity_df["category"].isin(["Tymarravail", "Comp Set RevPAR", "Tymktavail", "HBD RevPAR"]))]
		productivity_df_data.rename(columns = {"productivity_amount": "amount"}, inplace=True)

		goals_quater_rpi_calculations = quarter_rpi_calculations(goals_df_data)
		if not goals_quater_rpi_calculations["success"]: 
			return goals_quater_rpi_calculations
		
		goals_data_after_calc = goals_quater_rpi_calculations["df"]
		
		# goals_calc = goals_data_after_calc[["RPI"]].T
		# goals_reset_index = goals_calc.reset_index()
		# goals_reset_index.rename(columns = {0 : "goal"}, inplace = True)

		prod_quater_rpi_calculations = quarter_rpi_calculations(productivity_df_data)
		if not prod_quater_rpi_calculations["success"]: 
			return prod_quater_rpi_calculations
		
		prod_quater_after_calc = prod_quater_rpi_calculations["df"]
		
		merge_goals_productivity = pd.merge(goals_data_after_calc, prod_quater_after_calc, on=["marsha"], how="outer")
		merge_goals_productivity["achieved"] = (merge_goals_productivity["quarter_rpi_y"]/merge_goals_productivity["quarter_rpi_x"])*100
		merge_goals_productivity.rename(columns = {"quarter_rpi_x" : "goal", "quarter_rpi_y": "productivity"}, inplace = True)
		merge_goals_productivity = merge_goals_productivity.round(decimals = 2)
		merge_goals_productivity["category"] = "RPI"
		merge_goals_productivity.drop('marsha', axis=1, inplace=True)
		merge_goals_productivity.replace([np.nan,np.inf],0, inplace=True)

		return {"success": True, "df": merge_goals_productivity}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("quarter_rpi_calculations_goals_vs_prod", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}


def quarter_rm_cat_rev_calculations(goals_df, productivity_df, rmip=True):
	try:
		remove_rpi_from_goals = goals_df.loc[(goals_df["category"].isin(["Catering Rev", "RmRev"]))]
		remove_rpi_from_productivity = productivity_df.loc[(productivity_df["category"].isin(["Catering Rev", "RmRev"]))]
		
		group_goals = remove_rpi_from_goals.groupby(["marsha", "category"]).agg({"amount": "sum"}).reset_index()
		group_productivity = remove_rpi_from_productivity.groupby(["marsha", "category"]).agg({"productivity_amount": "sum"}).reset_index()

		pivot_goals = pd.pivot_table(group_goals, index= ['marsha'], columns = ['category'], values=['amount']).reset_index()
		pivot_goals = pivot_goals.droplevel(0, axis=1)
		pivot_goals.rename(columns = {"" : "marsha"}, inplace = True)

		pivot_productivity = pd.pivot_table(group_productivity, index= ['marsha'], columns = ['category'], values=['productivity_amount']).reset_index()
		pivot_productivity = pivot_productivity.droplevel(0, axis=1)
		pivot_productivity.rename(columns = {"" : "marsha", "RmRev": "Productivity RmRev", "RevPAR": "Productivity RevPAR", "Catering Rev": "Productivity Catering Rev"}, inplace = True)

		merge_goals_productivity = pd.merge(pivot_goals, pivot_productivity, on=["marsha"], how="outer")
		merge_goals_productivity.replace(np.nan,0, inplace=True)

		merge_goals_productivity["rmrev_achieved"] = (merge_goals_productivity["Productivity RmRev"] / merge_goals_productivity["RmRev"])*100
		merge_goals_productivity["catering_rev_achieved"] = (merge_goals_productivity["Productivity Catering Rev"] / merge_goals_productivity["Catering Rev"]) * 100

		
		merge_goals_productivity.replace(np.nan,0, inplace=True)
		round_df = merge_goals_productivity.round(decimals = 2)
		if rmip == False:
			goals_calc = round_df[["Catering Rev", "RmRev"]].T
			goals_reset_index = goals_calc.reset_index()
			goals_reset_index.rename(columns = {0 : "goal"}, inplace = True)

			productivity_calc = round_df[["Productivity Catering Rev", "Productivity RmRev"]].T
			productivity_reset_index = productivity_calc.reset_index()
			productivity_reset_index.rename(columns = {0 : "productivity"}, inplace = True)
			productivity_reset_index.category.replace(["Productivity Catering Rev", "Productivity RmRev"], ["Catering Rev", "RmRev"], inplace=True)

			achieved_calc = round_df[["catering_rev_achieved", "rmrev_achieved"]].T
			achieved_reset_index = achieved_calc.reset_index()
			achieved_reset_index.rename(columns = {0 : "achieved"}, inplace = True)
			achieved_reset_index.category.replace(["catering_rev_achieved", "rmrev_achieved"], ["Catering Rev", "RmRev"], inplace=True)

			merge_total_df = pd.merge(pd.merge(goals_reset_index, productivity_reset_index, on=["category"], how="outer"), achieved_reset_index, on=["category"], how="outer")
			merge_total_df.replace(np.nan,0, inplace=True)
			return {"success": True, "df": merge_total_df}
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("quarter_rm_cat_rev_calculations", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "message": str(e)}