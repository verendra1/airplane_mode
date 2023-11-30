import frappe
import sys, traceback
import pandas as pd
from revenue_management.utlis import get_quarter_details


@frappe.whitelist()
def rmip_calculations(eid=None, quarter=None, year=None):
    try:
        get_team_member = frappe.db.get_value("Team Members", {"eid": eid, "year": year}, ["name"])
        if get_team_member:
            get_quarter = get_quarter_details(quarter)
            if not get_quarter["success"]:
                return get_quarter
            get_supporting_marsha = frappe.db.get_list("Supporting Marsha", filters={"parent": get_team_member}, pluck="marsha")
            if len(get_supporting_marsha) == 0:
                return {"success": False, "message": "no supporting marsha assigned"}
            get_marsha_details = frappe.db.get_list("Marsha Details", filters=[["name", "in", get_supporting_marsha]], fields=["marsha", "market_share_type", "ms_comp_non_comp"])
            get_goals_data = frappe.db.get_list("Goals", filters=[["month", "in", get_quarter["months"]], ["year", "=", year], ["marsha", "in", get_supporting_marsha], ["category", "in", ["RmRev", "Catering Rev", "RPI", "RevPAR"]]], fields=["category", "marsha","amount"])
            if len(get_goals_data) == 0:
                return {"success": False, "message": "no goals found"}
            get_productivity_data = frappe.db.get_list("Productivity", filters=[["month", "in", get_quarter["months"]], ["year", "=", year], ["marsha", "in", get_supporting_marsha], ["category", "in", ["RmRev", "Catering Rev", "RPI", "RevPAR"]]], fields=["category", "marsha","amount"])

            if len(get_productivity_data) == 0:
                return {"success": False, "message": "no productivity found"}
            
            marsha_df = pd.DataFrame.from_records(get_marsha_details)
            goals_df = pd.DataFrame.from_records(get_goals_data)
            productivity_df = pd.DataFrame.from_records(get_productivity_data)
            
            rmrev_catering_from_goals_df = goals_df.loc[goals_df['category'].isin(["RmRev", "Catering Rev"])]
            rmrev_catering_from_productivity_df = productivity_df.loc[productivity_df['category'].isin(["RmRev", "Catering Rev"])]

            group_rmrev_catering_from_goals_df = rmrev_catering_from_goals_df.groupby(["marsha", "category"]).agg({"amount": "sum"}).reset_index()

            group_rmrev_catering_from_productivity_df = rmrev_catering_from_productivity_df.groupby(["marsha", "category"]).agg({"amount": "sum"}).reset_index()

            

    #         merge_goals_with_marshas = pd.merge(goals_df, marsha_df, on=["marsha"])
    #         merge_productivity_with_marshas = pd.merge(productivity_df, marsha_df, on=["marsha"])

    #         filter_rpi_in_goals = merge_goals_with_marshas.loc[(merge_goals_with_marshas['ms_comp_non_comp'] == 'Y') & (merge_goals_with_marshas['market_share_type'] == 'SB') & (merge_goals_with_marshas["category"] != "RevPar")]
    #         filter_rpi_in_productivity = merge_productivity_with_marshas.loc[(merge_productivity_with_marshas['ms_comp_non_comp'] == 'Y') & (merge_productivity_with_marshas['market_share_type'] == 'SB') & (merge_productivity_with_marshas["category"] != "RevPar")]

    #         filter_revpar_in_goals = merge_goals_with_marshas.loc[(merge_goals_with_marshas['ms_comp_non_comp'] != 'Y') & (merge_goals_with_marshas['market_share_type'] != 'SB') & (merge_goals_with_marshas["category"] != "RPI")]
    #         filter_revpar_in_productivity = merge_productivity_with_marshas.loc[(merge_productivity_with_marshas['ms_comp_non_comp'] != 'Y') & (merge_productivity_with_marshas['market_share_type'] != 'SB') & (merge_productivity_with_marshas["category"] != "RPI")]
            
    #         only_columns = ["category", "marsha", "amount"]

    #         if len(filter_rpi_in_goals) > 0:
    #             pass

            if len(group_rmrev_catering_from_goals_df) > 0 and len(group_rmrev_catering_from_productivity_df) > 0:
                pivot_goals = pd.pivot_table(group_rmrev_catering_from_goals_df, index= ['marsha'], columns = ['category'], values=['amount']).reset_index()
                pivot_goals = pivot_goals.droplevel(0, axis=1)
                pivot_goals.rename(columns = {"" : "marsha"}, inplace = True)

                pivot_productivity = pd.pivot_table(group_rmrev_catering_from_productivity_df, index= ['marsha'], columns = ['category'], values=['amount']).reset_index()
                pivot_productivity = pivot_productivity.droplevel(0, axis=1)
                pivot_productivity.rename(columns = {"" : "marsha", "RmRev": "Productivity RmRev", "RevPAR": "Productivity RevPAR", "Catering Rev": "Productivity Catering Rev"}, inplace = True)

                merge_goals_productivity = pd.merge(pivot_goals, pivot_productivity, on=["marsha"])
                merge_goals_productivity["rmrev_achieved"] = (merge_goals_productivity["Productivity RmRev"] / merge_goals_productivity["RmRev"])*100
                # merge_goals_productivity["revpar_achieved"] = (merge_goals_productivity["Productivity RevPAR"] / merge_goals_productivity["RevPAR"]) * 100
                merge_goals_productivity["catering_rev_achieved"] = (merge_goals_productivity["Productivity Catering Rev"] / merge_goals_productivity["Catering Rev"]) * 100

                rmrev_total = merge_goals_productivity['RmRev'].sum()
                catering_rev = merge_goals_productivity["Catering Rev"].sum()

                merge_goals_productivity["rmrev_weightage"] = (merge_goals_productivity["RmRev"]/rmrev_total)*100
                merge_goals_productivity["catering_rev_weightage"] = (merge_goals_productivity["Catering Rev"] / catering_rev) * 100
                
                merge_goals_productivity['rmrev_earning'] = merge_goals_productivity.apply(lambda merge_goals_productivity: check_earnings(merge_goals_productivity["rmrev_achieved"]), axis = 1)
                merge_goals_productivity['catering_rev_earning'] = merge_goals_productivity.apply(lambda merge_goals_productivity: check_earnings(merge_goals_productivity["catering_rev_achieved"]), axis = 1)

                get_particular_columns = merge_goals_productivity[["marsha", "rmrev_weightage", "catering_rev_weightage", "rmrev_earning", "catering_rev_earning"]]
                get_particular_columns.set_index("marsha", inplace = True)
                get_particular_columns["earning_sum"] = get_particular_columns[['rmrev_earning', 'catering_rev_earning']].sum(axis=1)
                print(get_particular_columns.to_string())


                

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_team_leader_as_user", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}




def check_earnings(achieved_value):
    # try:
        if (achieved_value >= 100 and  achieved_value < 110):
            return 5
        elif (achieved_value >= 110 and  achieved_value < 120):
            return 10
        elif (achieved_value >= 120):
            return 20
        else:
            return 0
    # except Exception as e:
    #     pass