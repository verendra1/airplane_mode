import datetime
import frappe
import traceback
import requests
import sys, os
from frappe.utils import cstr
from frappe.core.doctype.data_import.data_import import form_start_import
from frappe.utils.password import check_password

def dataimport(file=None, import_type=None, reference_doctype=None):
    try:
        doc = {
            "doctype": "Data Import",
            "reference_doctype": reference_doctype,
            "import_type": import_type,
            "status": "Pending"
        }
        data = frappe.get_doc(doc)
        data.insert()
        frappe.db.commit()
        frappe.db.set_value("Data Import", data.name, "import_file", file)
        frappe.db.commit()
        data_import = data.name
        start_import = form_start_import(data_import)
        return {"success": True}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("dataimport", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}
    

def upload_file_api(filename = None):
    try:
        if filename:
            files = {"file": open(filename, 'rb')}
            payload = {'is_private': 1, 'folder': 'Home'}
            site_name = cstr(frappe.local.site)
            upload_qr_image = requests.post("https://"+site_name+ "/api/method/upload_file",
                                            files=files,
                                            data=payload, verify=False)
            response = upload_qr_image.json()
            if 'message' in response:
                os.remove(filename)
                file = response['message']['file_url']
                return {"success": True, "file": file}
            frappe.log_error("upload_file_api", response)
            return {"success": False, "message": response}
        return {"success": False, "message": "filename is missing"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("upload_file_api", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}



@frappe.whitelist(allow_guest=True)
def reset_initial_password(user):
    try:
        get_user_details = frappe.get_doc('User', {'username': user})
        if get_user_details.last_active == None and get_user_details.last_password_reset_date == None:
            return {'user': get_user_details.email, 'success': True, "message": "New login force to reset", "user_name": user}
        return {'user': get_user_details.email, 'success': False, "message": "Old login", "user_name": user}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("reset_initial_password", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"message": "Invalid User"}


@frappe.whitelist(allow_guest=True)
def change_old_password(user, pwd):
    try:
        confirm_pwd = check_password(
            user, pwd, doctype="User", fieldname="password", delete_tracker_cache=True)
        # confirm_pwd = confirm_pwd.strip()

        if confirm_pwd == user:
            return {'success': True, "message": "Password matched", "user_name": user}
        else:
            return {'success': False, "message": "Password not matched"}
    except Exception as e:
        return {"message": "Incorrect User or Password"}


@frappe.whitelist(allow_guest=True)
def update_pwd(email,last_password_reset_date,new_password,old_pwd):
    try:
        doc = frappe.get_doc("User", email)
        doc.last_password_reset_date = last_password_reset_date
        doc.new_password = new_password
        doc.old_pwd = old_pwd
        doc.save(ignore_permissions=True)
        return {"success":True}
    except Exception as e:
        return {"message":"Incorrect User or  Password"}


def create_user(email=None, user_name=None, first_name=None, last_name=None, role=None):
    try:
        if not frappe.db.exists("User", {"email": email}):
            user_data = {"first_name": first_name, "last_name": last_name, "username": user_name, "email": email, "user_type": "Website User", "enabled": 1, "doctype": "User", "send_welcome_email": 0, "new_password": "Welcome@123",
                            "roles": [{
                                "role": role,
                                "parent": role,
                                "parentfield": "roles",
                                "parenttype": "User",
                                "doctype": "Has Role"
                            }]}
            user_doc = frappe.get_doc(user_data)
            user_doc.insert()
            frappe.db.commit()
            return {"success": True ,"message": "user created successfully"}
        return {"success": False, "message": "user already exists"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_user", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}


def send_mail_to_user(content, email_id, subject):
    try:
        frappe.sendmail(
            recipients = email_id,
            cc = '',
            subject = subject,
            content = content,
            now = True
        )
        return {'success': True, "message": "mail sent successfully"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("send_mail_to_user", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}


def get_current_quarter_months():
    try:
        current_date = datetime.datetime.now()
        current_year = str(current_date.year)
        if 1 <= current_date.month <= 3:
            return {"success": True , "quarter": ["January "+current_year, "February "+current_year, "March "+current_year]}
        elif 4 <= current_date.month <= 6:
            return {"success": True , "quarter": ["April "+current_year, "May "+current_year, "June "+current_year]}
        elif 7 <= current_date.month <= 9:
            return {"success": True , "quarter": ["July "+current_year, "August "+current_year, "September "+current_year]}
        else:
            return {"success": True , "quarter": ["October "+current_year, "November "+current_year, "December "+current_year]}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_current_quarter_months", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_cluster_details():
    try:
        data = frappe.db.get_list("Cluster Details", pluck="name")
        if len(data) > 0:
            return {"success": True, "data": data}
        return {"success": False, "message": "no cluster details were found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_cluster_details", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}


def get_quarter_details(quater):
    try:
        if quater == "Q1":
            return {"success": True, "months": ["Jan", "Feb", "Mar"]}
        elif quater == "Q2":
            return {"success": True, "months": ["Apr", "May", "Jun"]}
        elif quater == "Q3":
            return {"success": True, "months": ["Jul", "Aug", "Sep"]}
        elif quater == "Q4":
            return {"success": True, "months": ["Oct", "Nov", "Dec"]}
        else:
            return {"success": False, "message": "quarter not found"} 
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_quarter_details", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}