
import frappe
from frappe.model.document import Document

class HairTalkSalon(Document):
    pass
@frappe.whitelist(allow_guest=True)
def documentapis():
    pass
#     doc=frappe.get_doc("Hair Talk Salon","Verendra")
#     doc=frappe.get_doc(
#         {
#             'doctype':"Hair Talk Salon",
#             'customer_name':'Sneha',
#             'service':'Hair Cut'
#         }
#     )

#     # doc3=frappe.get_last_doc("Hair Talk Salon")
#     # doc4=frappe.get_last_doc("Hair Talk Salon",filters = {"status":"Cancelled"})
#     # doc5=frappe.delete_doc("Hair Talk Salon","Ajay")
#     # doc.save()
#     doc.insert()
#     frappe.db.commit()
#     print(doc,"///////////////////////////")
#     task=frappe.get_last_doc("Hair Talk Salon")
#     task=frappe.get_last_doc("Hair Talk Salon",filters={"Status":"Cancelled"}, order_by="timestamp desc")
#     doc=frappe.new_doc("Hair Talk Salon")
#     doc.customer_name="swapna"
#     doc.insert()
#     frappe.db.commit()
#     doc=frappe.delete_doc("Hair Talk Salon","swapna")
#     frappe.db.commit()
#     doc=frappe.rename_doc("Hair Talk Salon",'sneha',"swapna")
#     frappe.db.commit()
#     doc=frappe.get_meta("Hair Talk Salon")
#     doc.get_custom_fields()
#     task=doc.get_url()
#     return task
#     return doc1

@frappe.whitelist(allow_guest=True)
def databaseapis():
    pass
    # doc=frappe.get_list("Hair Talk Salon")
    # doc=frappe.get_list("Hair Talk Salon",pluck='name')

    # doc=frappe.db.get_list("Hair Talk Salon",fields=["customer_name","service"])
    # doc=frappe.db.get_list("Hair Talk Salon",fields=["customer_name","service"],filters={"Top stylist"})

    # doc=frappe.get_all("Hair Talk Salon")

    # doc=frappe.get_value("Hair Talk Salon","Verendra","mobile_no")
    # doc=frappe.get_value("Hair Talk Salon","Verendra",["mobile_no","employee_name"])
    # doc=frappe.get_value("Hair Talk Salon","verendra",["mobile_no","employee_name"],as_dict=1)

    # doc=frappe.db.get_single_value("Hair Talk Salon","mobile_no")

    # doc=frappe.db.set_value("Hair Talk Salon","Verendra","mobile_no","9959837576")
    # doc=frappe.set_value("Hair Talk Salon","verendra",
    # {
    #     "mobile_no":"8106232046",
    #     "service":"root touch up"
    # })
    # doc=frappe.set_value("Hair Talk Salon","Verendra","mobile_no","6300232564", update_modified=False)

    # doc=frappe.db.exists("Hair Talk Salon","Verendra",cache=True)
    # doc=frappe.db.exists({"doctype":"Hair Talk Salon","customer_name":"Verendra"})
    # doc=frappe.db.exists("Hair Talk Salon",{"customer_name":"Verendra"})

    # doc=frappe.db.count("Hair Talk Salon")
    # doc=frappe.db.count("Hair Talk Salon",{"customer_name":"Verendra"})

    # frappe.db.delete("ram")
    # frappe.db.truncate("ram")
    # frappe.db.commit()

    # csk=["Ruturaj Gaikwad","Devon conway","Ajinkya Rahane","Shivam Dube","Ravindra Jadeja","MS Dhoni(C)","Patherana","Deepak Chahar","Mukesh Choudary","Maheesh Teekshana","Shardhul Thakur"]
    # Batsman=["Ruturaj Gaikwad","Devon conway","Ajinkya Rahane","MS Dhoni(C)"]

    return doc











# method=documentapis()


    # csk=["rayudu","chahar"]
    # if "rayudu" in csk:
    # 	print("yes")
    # else:
    # 	print("No")

    # path_for_l124 = "L124_"+company+"_"+user

    #     output_file_path_for_L124 = invoice_file + \
    #             "/private/files/"+path_for_l124+"_"+f"{period}.xlsx"
    #     # data.to_excel(output_file_path_for_L124,index=False)
    #     data_frame_l124.to_excel(output_file_path_for_L124,index=False)

    #     files_for_l124 = {"file": open(output_file_path_for_L124, 'rb')}
    #     payload = {'is_private': 1, 'folder': 'Home'}

    #     frappe.db.delete("AR L124", {
    #                         "hospitality_unit_name": company,
    #                         "period": f"{period}",
    #                     })
    #     frappe.db.commit()
    #     upload_j104_excel_file_L124 = requests.post("http://"+ "0.0.0.0:8000" + "/api/method/upload_file",
    #                                         files=files_for_l124,
    #                                         data=payload)
        
    #     response = upload_j104_excel_file_L124.json()
    #     if 'message' in response:
    #         os.remove(output_file_path_for_L124)
                
        
    #     file_after_response_L124 = response['message']['file_url']
    #     doc = {
    #                 "doctype": "Data Import",
    #                 "reference_doctype": "AR L124",
    #                 "custom_hospitality_unit": company,
    #                 "import_type": "Insert New Records",
    #                 # "import_file": file,
    #                 "status": "Pending"
    #                 }
    #     data = frappe.get_doc(doc)
    #     data.insert()
    #     frappe.db.commit()


    #     frappe.db.set_value("Data Import", data.name, "import_file", file_after_response_L124)
    #     frappe.db.commit()
    #     data_import = data.name
    #     form_start_import(data_import)
    	# form_start_import(data_import)


