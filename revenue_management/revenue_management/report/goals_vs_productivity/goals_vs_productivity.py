# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import sys, traceback
import pandas as pd
import numpy as np
from revenue_management.utlis import get_quarter_details


def execute(filters=None):
    columns, data = [], []
    print(goal_vs_productivity(filters))
    return columns, data


def goal_vs_productivity(filters):
    try:
        get_goals = frappe.db.get_list("Goals", filters=filters, fields=["marsha", "category", "amount"])
        get_productivity  = frappe.db.get_list("Productivity", filters=filters, fields=["marsha", "category", "amount as productivity_amount"])
        if len(get_productivity) == 0 or len(get_goals) == 0:
            return []
        marsha_details = frappe.db.get_list("Marsha Details", fields=["marsha", "market_share_type", "ms_comp_non_comp"])
        marsha_df = pd.DataFrame.from_records(marsha_details)

        goals_df = pd.DataFrame.from_records(get_goals)
        goals_df = goals_df.loc[(goals_df["category"].isin(["RPI", "RevPAR", "Catering Rev", "RmRev"]))]

        productivity_df = pd.DataFrame.from_records(get_productivity)
        productivity_df = productivity_df.loc[(productivity_df["category"].isin(["RPI", "RevPAR", "Catering Rev", "RmRev"]))]

        merge_df = pd.merge(goals_df, marsha_df, on=["marsha"])
        goals_rpi = merge_df.loc[(merge_df['ms_comp_non_comp'] == 'Y') & (merge_df['market_share_type'] == 'SB')  & (merge_df["category"] != 'RevPAR')]
        goals_revpar = merge_df.loc[(merge_df['ms_comp_non_comp'] != 'Y') & (merge_df['market_share_type'] != 'SB')  & (merge_df["category"] != 'RPI')]
        merge_goals = pd.concat([goals_rpi, goals_revpar])
        merge_goals = merge_goals[["marsha", "category", "amount"]]
        pivot_goals = pd.pivot_table(merge_goals, index= ['marsha'], columns = ['category'], values=['amount']).reset_index()
        pivot_goals_df = pivot_goals.droplevel(0, axis=1)
        pivot_goals_df.rename(columns = {"" : "marsha"}, inplace = True)

        merge_productivity_df = pd.merge(productivity_df, marsha_df, on=["marsha"])
        productivity_rpi = merge_productivity_df.loc[(merge_productivity_df['ms_comp_non_comp'] == 'Y') & (merge_productivity_df['market_share_type'] == 'SB')  & (merge_productivity_df["category"] != 'RevPAR')]
        productivity_revpar = merge_productivity_df.loc[(merge_productivity_df['ms_comp_non_comp'] != 'Y') & (merge_productivity_df['market_share_type'] != 'SB')]
        merge_productivity = pd.concat([productivity_rpi, productivity_revpar])
        merge_productivity = merge_productivity[["marsha", "category", "productivity_amount"]]
        pivot_productivity = pd.pivot_table(merge_productivity, index= ['marsha'], columns = ['category'], values=['productivity_amount']).reset_index()
        pivot_productivity_df = pivot_productivity.droplevel(0, axis=1)
        pivot_productivity_df.rename(columns = {"" : "marsha", "RPI": "productivity_RPI", "Catering Rev": "productivity_Catering_Rev", "RevPAR": "productivity_RevPAR", "RmRev": "productivity_RmRev"}, inplace = True)
        merge_both = pd.merge(pivot_goals_df, pivot_productivity_df, on=['marsha'], how="outer")
        merge_both.replace(np.nan,0, inplace=True)
        merge_both = merge_both.round(decimals = 2)
        merge_both["catering_rev_weightage"] = (merge_both["productivity_Catering_Rev"]/merge_both["Catering Rev"])*100
        merge_both["rmrev_weightage"] = (merge_both["productivity_RmRev"]/merge_both["RmRev"])*100
        merge_both["revpar_weightage"] = (merge_both["productivity_RevPAR"]/merge_both["RevPAR"])*100
        merge_both["rpi_weightage"] = (merge_both["productivity_RPI"]/merge_both["RPI"])*100
        merge_both = merge_both.round(decimals = 2)
        merge_both.replace(np.nan,0, inplace=True)
        merge_both = merge_both[["marsha", "productivity_RmRev", "RmRev", "rmrev_weightage", "productivity_Catering_Rev","Catering Rev", "catering_rev_weightage", "productivity_RevPAR", "RevPAR", "revpar_weightage", "productivity_RPI", "RPI", "rpi_weightage"]]
        split_goals_df = merge_both[["marsha", "productivity_RmRev", "RmRev", "rmrev_weightage"]]
        # merge_both.to_excel("/home/caratred/test.xlsx", index=False)
        # data = merge_both.to_dict('records')
        # return data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("goal_vs_productivity", "line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}