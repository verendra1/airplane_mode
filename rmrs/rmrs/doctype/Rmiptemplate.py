# import pandas as pd
# import frappe
# import xlsxwriter

# def get_col_widths(dataframe):
#     widths = []
#     for col in dataframe.columns:
#         max_length = max(dataframe[col].astype(str).map(len).max(), len(col))
#         widths.append(max_length)
#     return widths

# @frappe.whitelist(allow_guest=True)
# def rmiptemplate():
#     dfs = {
#         "Room Revenue": ["Marsha", "Room Revenue Component", "Room Actuals", "Room Goal/ Budget", "B/(W)", "% Achievement", "% Payout", "Payout(in INR)"],
#         "Catering Revenue": ["Marsha", "Catering Revenue Component", "Catering Actuals", "Catering Goal/ Budget", "B/(W)", "% Achievement", "% Payout", "Payout(in INR)"],
#         "Revpar Index": ["Marsha", "Matrix", "RevPAR Index Actuals", "RevPAR Index Goal", "B/(W)", "% Achievement", "% Payout", "Payout (in INR)"],
#         "Payout Breakdown by Component and Property":["Marsha","HRO","Actuals","Goal","B/(W)","% Achievement","% Payout","Payout(in INR)"],
#         "Gatekeeper: Room & Catering Revenue":["Marsha","Property","Actual","Budget","B/(W)","% Achievement","Exceeded Gatekeeper"]
#     }
   
#     excel_file_path = '/home/verendra/Downloads/RMIPTEMPLATE.xlsx'
#     with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
#         workbook = writer.book
#         worksheet = workbook.add_worksheet('All_DataFrames')
#         cell_format = workbook.add_format({'bold': True,'bg_color': '#4682B4', 'border': 1,'font_color': 'white','font_size': 9})

#         bold_format = workbook.add_format({'bold': True, 'bg_color':'#F0FFFF', 'font_color': 'black','font_size': 9})
#         merge_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#1874CD', 'font_color': 'white', 'font_size': 13})
#         box_format = workbook.add_format({'border': 1})  
#         worksheet.merge_range(1, 0, 0, 7, "Revenue Management Incentive Plan", merge_format)
#         worksheet.merge_range(3, 0, 3, 1, "Property/Cluster Name:", bold_format)
#         worksheet.merge_range(4, 0, 4, 1, "Employee Name:", bold_format)
#         worksheet.merge_range(5, 0, 5, 1, "Employee ID:     ", bold_format)
#         worksheet.merge_range(6, 0, 6, 1, "Title:     ", bold_format)

#         worksheet.merge_range(3, 2, 3, 7, "Participant Plan:     ", bold_format)
#         worksheet.merge_range(4, 2, 4, 7, "Maximum:    ", bold_format)
#         worksheet.merge_range(5, 2, 5, 7, "Plan Frequency:     ", bold_format)
#         worksheet.merge_range(6, 2, 6, 7, "Timeframe:     ", bold_format)

#         worksheet.merge_range(8, 0, 8 ,1, "Eligible Earnings:     ", bold_format)
#         worksheet.merge_range(9, 0, 9, 1,  "Local Currency:    ", bold_format)
#         worksheet.merge_range(10, 0, 10, 1,  "Hotels Supported:     ", bold_format)

#         worksheet.merge_range(8, 2, 8, 7, "Final Dates of Eligibility During Incentive Period:     ", bold_format)
#         worksheet.merge_range(9, 2, 9 ,7, "Start", bold_format)
#         worksheet.merge_range(10, 2, 10 ,7, "End", bold_format)

#         worksheet.merge_range(78,0,78,1, "Associate		                                                                                   Date",bold_format)
#         worksheet.merge_range(78,2,78,6, "Revenue Leader	                                                                         Date",bold_format)
#         worksheet.merge_range(80,0,80,1, "Finance Leader	                                                                         Date",bold_format)
#         worksheet.merge_range(80,2,80,6, "General Leader	                                                                         Date",bold_format)
              
#         start_row = 13 
#         start_col = 0
#         for label, columns in dfs.items():
#             df = pd.DataFrame(columns=columns)

#             worksheet.write(start_row - 1, start_col, label, cell_format)
#             df.to_excel(writer, sheet_name='All_DataFrames', startrow=start_row, startcol=start_col, index=False)
#             end_row = start_row + len(df.index)
#             end_col = start_col + len(df.columns) 
#             worksheet.add_table(start_row, start_col, end_row, end_col, {'style': 'Table Style Medium 10'})

#             for col_idx, value in enumerate(df.columns.values):
#                 worksheet.write(start_row, start_col + col_idx, value, cell_format)

#             for i, width in enumerate(get_col_widths(df)):
#                 worksheet.set_column(start_col + i, start_col + i, width)
#             start_row = end_row + 13
            
#     return excel_file_path
    
# # generated_file = rmiptemplate()
# try:
#     generated_file = rmiptemplate()
#     print(f"Excel file generated at: {generated_file}")
# except Exception as e:
#     print(f"Error generating Excel file: {e}")



import frappe
from frappe import _
from frappe.model.document import Document

def execute(filters=None):
    columns = [
        {
            "label": _("Empname"),
            "fieldname": "empname",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Email"),
            "fieldname": "email",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Mobile"),
            "fieldname": "mobile",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Salary"),
            "fieldname": "salary",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Designation",
            "fieldname": "designation",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Data",
            "width": 150
        }
    ]

    data = []
    if filters:
        filter_conditions = []

        # Add filter conditions based on the user's input fields
        if filters.get("company"):
            # filter_conditions.append(f"`tabEmp Salary List`.`company` = '{filters.get('company')}'")
              filter_conditions.append(f"""E3.company = '{filters.get('company')}'""")
        if filters.get("designation"):
            # filter_conditions.append(f"`tabEmp Salary List`.`designation` = '{filters.get('designation')}'")
            filter_conditions.append(f"""E1.designation = '{filters.get('designation')}'""")
            print(filter_conditions,"111111111111111111111111111111111111111111")
        filter_query = " AND ".join(filter_conditions)
        print(filter_query,"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        query = f"""
                SELECT 
                    E1.empname,
                    E2.email,
                    E2.mobile,
                    E1.salary,
                    E1.designation,
                    E3.company
                FROM
                    `tabEmp Salary List` E1
                CROSS JOIN
                    `tabEMP Contact` E2 ON E1.empname = E2.employeename
                JOIN
                    `tabEmp List` E3 ON E1.empname = E3.name_of_the_employ
                WHERE
                   {filter_query}
                """
            # WHERE
            #    {filter_query}
            
        mixing_data = frappe.db.sql(query, as_dict=True)

        for row in mixing_data:
                data.append({
                    "empname": row["empname"],
                    "email": row["email"],
                    "mobile": row["mobile"],
                    "salary": row["salary"],
                    "designation": row["designation"],
                    "company": row["company"]
                })

    else:
        query = f"""
            SELECT 
                E1.empname,
                E2.email,
                E2.mobile,
                E1.salary,
                E1.designation,
                E3.company
            FROM
                `tabEmp Salary List` E1
            CROSS JOIN
                `tabEMP Contact` E2 ON E1.empname = E2.employeename
            JOIN
                `tabEmp List` E3 ON E1.empname = E3.name_of_the_employ
            
        """
        
        mixing_data = frappe.db.sql(query, as_dict=True)

        for row in mixing_data:
            data.append({
                "empname": row["empname"],
                "email": row["email"],
                "mobile": row["mobile"],
                "salary": row["salary"],
                "designation": row["designation"],
                "company": row["company"]
            })

    print(mixing_data,"*****************************************************************************************")