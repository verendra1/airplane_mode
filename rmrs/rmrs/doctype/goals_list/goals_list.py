# Copyright (c) 2023, verendra and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import pandas as pd
class GoalsList(Document):
	pass
	
@frappe.whitelist()
def workflows(record, action, reason=None, attachments=None):
    try:
        print("????????????????????????????")
        doc_of_rmrs_project = frappe.get_doc("Goals", record)
        doc_to_send = doc_of_rmrs_project.as_dict()
        print(doc_to_send, ")))))))))))))))))))))))))))))))))")
        df_rmrs_project = pd.DataFrame(doc_to_send, index=[0])

        if not frappe.db.exists({"doctype": "RMRS Rejection Reason", "docname": doc_to_send.name}):
            doc = frappe.get_doc({"doctype": "RMRS Rejection Reason", "docname": doc_to_send.name, "reason": reason})
            doc.insert()
            frappe.db.commit()
        else:
            document = frappe.get_doc("RMRS Rejection Reason", {"docname": doc_to_send.name, "reason": reason})
            document.save()
            frappe.db.commit()
            return {"message": "Fields are updated"}

        if not frappe.db.exists({"doctype": "RMRS Attachments", "docname": doc_to_send.name}):
            doc = frappe.get_doc({"doctype": "RMRS Attachments", "docname": doc_to_send.name, "attachments": attachments})
            doc.insert()
            frappe.db.commit()
            return {"message": "Attachments added successfully"}

        try:
            print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
            apply_workflow(doc=doc_to_send, action=action, attachments=attachments)
            frappe.db.commit()
            doc_of_rmrs_project.reload()
        except Exception as e:
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
            return {"message": str(e)}

        return {"message": "Workflow applied successfully"}
    except Exception as e:
        return {"message": str(e)}
