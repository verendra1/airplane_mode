# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import frappe
import sys, traceback
from frappe.model.document import Document
from revenue_management.utlis import create_user, send_mail_to_user


class Approvers(Document):
    pass


def create_approver_as_user(doc, method=None):
    try:
        frappe.db.set_value("Employees", doc.eid, "added_as_approver", 1)
        frappe.db.commit()
        user_creation = create_user(email=doc.email, user_name=doc.eid, first_name=doc.first_name, last_name=doc.last_name, role="Approver")
        if not user_creation["success"]:
            return user_creation
        user_doc = frappe.get_doc("User", doc.email)
        if user_doc:
            b2csuccess = frappe.get_doc('Email Template',"Team Leader Login Details")
            message = b2csuccess.response
            replace_first_name = message.replace("[first_name]", user_doc.first_name)
            replace_email = replace_first_name.replace("[email_id]", user_doc.email)
            send_mail_to_user(content=replace_email, email_id=user_doc.email, subject=b2csuccess.subject)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_team_leader_as_user", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}
