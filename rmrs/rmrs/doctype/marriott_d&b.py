

































# import frappe
# import pandas as pd
# from difflib import SequenceMatcher
# import numpy as np


# @frappe.whitelist(allow_guest=True)
# def comparing_two_columns():
#     data = pd.read_csv("/home/verendra/Downloads/aragingdet9573418-30.09.23.txt", delimiter='\t')
#     data1 = pd.read_excel("/home/verendra/Downloads/Marriott_MIS (D&B list).xlsx")
#     account = data["ACCOUNT_NAME"]
#     name = data1["Name of the case"]
#     comparison=data["ACCOUNT_NAME"].isin( data1["Name of the case"])
#     print(comparison)
#     return comparison                                                 



# import frappe
# import pandas as pd
# from difflib import SequenceMatcher

# @frappe.whitelist(allow_guest=True)
# def comparing_two_columns():
#     data = pd.read_csv("/home/verendra/Downloads/aragingdet9573418-30.09.23.txt", delimiter='\t')
#     data1 = pd.read_excel("/home/verendra/Downloads/Marriott_MIS (D&B list).xlsx")       
#     if "ACCOUNT_NAME" in data.columns and "Name of the case" in data1.columns:
#         account = data["ACCOUNT_NAME"]
#         name = data1["Name of the case"]           
#         def compare(account, name):           
#             match_score = SequenceMatcher(None, str(account), str(name)).ratio()
#             if match_score == 1.0:
#                 return "Full Match"
#             elif match_score >= 0.2:
#                 return "Partial Match"
#             else:
#                 return "No Match"
#         comparison_df = pd.DataFrame({'account': account, 'name': name})
#         comparison_df["result"] = comparison_df.apply(lambda row: compare(row['account'], row['name']), axis=1)
#         final=comparison_df.to_excel("/home/verendra/Downloads/comarison.xlsx")
#         print(comparison_df)           
#         return comparison_df

# comparison = comparing_two_columns()



# path_for_l124 = "L124_"+company+"_"+user

#         output_file_path_for_L124 = invoice_file + \
#                 "/private/files/"+path_for_l124+"_"+f"{period}.xlsx"
#         # data.to_excel(output_file_path_for_L124,index=False)
#         data_frame_l124.to_excel(output_file_path_for_L124,index=False)

#         files_for_l124 = {"file": open(output_file_path_for_L124, 'rb')}
#         payload = {'is_private': 1, 'folder': 'Home'}

#         frappe.db.delete("AR L124", {
#                             "hospitality_unit_name": company,
#                             "period": f"{period}",
#                         })
#         frappe.db.commit()
#         upload_j104_excel_file_L124 = requests.post("http://"+ "0.0.0.0:8000" + "/api/method/upload_file",
#                                             files=files_for_l124,
#                                             data=payload)
        
#         response = upload_j104_excel_file_L124.json()
#         if 'message' in response:
#             os.remove(output_file_path_for_L124)
                
        
#         file_after_response_L124 = response['message']['file_url']
#         doc = {
#                     "doctype": "Data Import",
#                     "reference_doctype": "AR L124",
#                     "custom_hospitality_unit": company,
#                     "import_type": "Insert New Records",
#                     # "import_file": file,
#                     "status": "Pending"
#                     }
#         data = frappe.get_doc(doc)
#         data.insert()
#         frappe.db.commit()


#         frappe.db.set_value("Data Import", data.name, "import_file", file_after_response_L124)
#         frappe.db.commit()
#         data_import = data.name
#         form_start_import(data_import)