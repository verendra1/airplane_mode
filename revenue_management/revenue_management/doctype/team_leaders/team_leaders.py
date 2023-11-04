# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import sys
import traceback
from frappe.model.document import Document


class TeamLeaders(Document):
    pass


def create_team_leader_as_user(doc, method=None):
    try:
        if not frappe.db.exists("User", {"email": doc.email_id}):
            user_data = {"first_name": doc.revenue_leader, "username": doc.eid, "email": doc.email_id, "user_type": "Website User", "enabled": 1, "doctype": "User", "send_welcome_email": 0, "new_password": "Welcome@123",
                         "roles": [{
                            "role": "Team Lead",
                            "parent": "Team Lead",
                            "parentfield": "roles",
                            "parenttype": "User",
                            "doctype": "Has Role"
                         }]}
            user_doc = frappe.get_doc(user_data)
            user_doc.insert(ignore_permissions=True, ignore_links=True)
            frappe.db.commit()
            # if user_doc.name:
            #     b2csuccess = frappe.get_doc('Email Template',"Team Leader Login Details")
            #     message = b2csuccess.response
            #     replace_first_name = message.replace("[first_name]", user_doc.first_name)
            #     replace_email = replace_first_name.replace("[email_id]", user_doc.email)
            #     frappe.sendmail(
            # 		recipients = user_doc.email,
            # 		cc = '',
            # 		subject = b2csuccess.subject,
            # 		content = replace_email,
            # 		now = True
            # 	)
            # return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_team_leader_as_user", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}
