# import requests
# import pandas as pd
# import frappe
# import json


# from revenue_management.revenue_management.doctype.calculations.goals_vs_productivity import goal_vs_productivity

# @frappe.whitelist(allow_guest=True)
# def goalsproductivity():
#     print("^^^^^^^^^^^^^")
#     data = goal_vs_productivity({"marsha":"HBALC","quarter":"Q1","year":2023})
#     print(data,"****")

#     quarter_df = pd.DataFrame(data['quarter_wise_data'])
#     print(quarter_df,"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$44")

#     month_df = pd.DataFrame([entry for sublist in data['month_wise_data'] for entry in sublist])
#     print(month_df)

#     quarter_excel=df.to_excel("/home/verendra/Downloads/quarter_wise_datas.xlsx",index=False)

#     month_excel=df.to_excel("/home/verendra/Downloads/quarter_wise_datas.xlsx",index=False)

#     return month_df





import pandas as pd
import frappe
from revenue_management.revenue_management.doctype.calculations.goals_vs_productivity import goal_vs_productivity

@frappe.whitelist(allow_guest=True)
def goalsproductivity():
    data = goal_vs_productivity({"marsha": "HBALC", "quarter": "Q1", "year": 2023})
    print(data,"?????????????????????????????????????????????????????")

    quarter_df = pd.DataFrame(data['quarter_wise_data'])
    quarter_excel_path = "/home/verendra/Downloads/quarter_wise_datas.xlsx"
    quarter_df.to_excel(quarter_excel_path, index=False)

    month_df = pd.DataFrame([entry for sublist in data['month_wise_data'] for entry in sublist])
    month_excel_path = "/home/verendra/Downloads/month_wise_datas.xlsx"
    month_df.to_excel(month_excel_path, index=False)

    return month_df


    # login_url = "https://rmnmt.ezyinvoicing.com/api/method/login"
    # login_data = {"usr": "sowmya123", "pwd": "Welcome@12345"}   
    # session = requests.Session()
    # response = session.post(login_url, data=login_data)
    
    # data = {"filters":{"marsha":"HBALC","quarter":"Q1","year":2023}}
    # url="https://rmnmt.ezyinvoicing.com/api/method/revenue_management.revenue_management.doctype.calculations.goals_vs_productivity.goal_vs_productivity"
    # responses = requests.get(url,data=data,stream=True)
    # print(responses.json())
    # return responses.json()



# import pandas as pd
# import frappe
# from revenue_management.revenue_management.doctype.calculations.goals_vs_productivity import goal_vs_productivity

# @frappe.whitelist(allow_guest=True)
# def goalsproductivity():
#     data = goal_vs_productivity({"marsha": "HBALC", "quarter": "Q1", "year": 2023})

#     df = pd.DataFrame(data)
    
#     writer = pd.ExcelWriter("/home/verendra/Downloads/GoalsProduc.xlsx", engine='xlsxwriter')
    
#     df.to_excel(writer, index=False)
#     writer.save()

#     return df





















