# Copyright (c) 2023, Caratred Technologies and contributors
# For license information, please see license.txt

import datetime
import frappe
import json
import sys, traceback
from frappe.model.document import Document
from revenue_management.utlis import create_user, send_mail_to_user


class TeamRoster(Document):
    pass


@frappe.whitelist()
def create_team(data):
    try:
        if isinstance(data, str):
            data = json.loads(data)

        current_date = datetime.datetime.today().strftime('%Y')
        current_date = current_date+"-01-01"
        employee_data = frappe.get_doc("Employees", data["eid"])
        if employee_data.job_name == "Voyage-AP-Revenue":
            eligibility = "Brilliant"
        else:
            if employee_data.career_band == "Purple":
                eligibility = "Golden Circle-Top Performer"
            else:
                eligibility = "RMIP-Golden Circle-Top Performer"
        get_role_effective_date = check_role_effective_date(job_date = employee_data.job_entry_date, job_name = employee_data.job_name)
        if "success" in get_role_effective_date:
            return get_role_effective_date
        role_effective_date = get_role_effective_date
        
        if frappe.db.exists("Team Leaders", data["eid"]):
            team_leader_data = frappe.get_doc("Team Leaders", data["eid"])
            team_leader_property_details = frappe.db.get_list("Marsha Details", filters={"cluster": data["cluster"]}, fields=["marsha"])
            create_teamroster = create_team_roster(
                {"cluster": team_leader_data.cluster})
            if not create_teamroster["success"]:
                return create_teamroster
            team_member_name = (employee_data.first_name if employee_data.first_name else "") + \
                " " + (employee_data.last_name if employee_data.last_name else "")

            team_members = {"eid": employee_data.name, "current_role_type": "Leader",
                            "team_member": team_member_name, "role_effective_date": role_effective_date,
                            "program_role": "Leader", "billing_marsha": None, "title": employee_data.job_name,
                            "team_roster": create_teamroster["name"], "supporting_marsha": team_leader_property_details, "eligibility": eligibility}
            team_member = create_team_members(team_members)
            if not team_member["success"]:
                return team_member
            return {"success": True, "message": "team member created"}
        else:
            employee_data = frappe.get_doc("Employees", data["eid"])

            team_member_name = (employee_data.first_name if employee_data.first_name else "") + \
                " " + (employee_data.last_name if employee_data.last_name else "")

            team_members = {"eid": employee_data.name, "current_role_type": "Individual Contributor",
                            "team_member": team_member_name, "role_effective_date": role_effective_date,
                            "program_role": "Individual Contributor", "billing_marsha": None, "title": employee_data.job_name,
                            "team_roster": data["team_roster_id"], "supporting_marsha": data["supporting_marsha"] if "supporting_marsha" in data else [],  "eligibility": eligibility}
            team_member = create_team_members(team_members)
            if not team_member["success"]:
                return team_member
            return {"success": True, "message": "team member created"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_team", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}


def create_team_roster(data={}):
    try:
        if len(data) > 0:
            today = datetime.date.today()
            data["doctype"] = "Team Roster"
            data["year"] = today.year
            if not frappe.db.exists("Team Roster", {"cluster": data["cluster"], "year": today.year}):
                doc = frappe.get_doc(data)
                doc.insert()
                frappe.db.commit()
                return {'success': True, "name": doc.name}
            return {"success": False, "name": "team roster already exists"}
        return {'success': False, "message": "team roster creation data is empty"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_team_roster", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}


def create_team_members(data={}):
    try:
        if len(data) > 0:
            data["doctype"] = "Team Members"
            if not frappe.db.exists("Team Members", {"eid": data["eid"], "status": "active"}):
                doc = frappe.get_doc(data)
                doc.insert()
                frappe.db.commit()
                if doc.name:
                    create_user_for_team_member(doc.as_dict())
                return {'success': True, "name": doc.name}
            return {"success": False, "message": "employee already exists in another team"}
        return {"success": False, "message": "team members creation data is empty"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_team_members", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_team_roster_details(cluster=None):
    try:
        get_team_roster_details = frappe.db.get_value("Team Roster", {"cluster": cluster}, ['name', "cluster", "year"], as_dict=True)
        if get_team_roster_details:
            get_team_members = frappe.db.get_list("Team Members", filters={"team_roster": get_team_roster_details["name"]}, fields={"*"})
            get_team_roster_details["team_members"] = get_team_members
            for each in get_team_members:
                get_supporting_masha = frappe.db.get_all("Supporting Marsha", {'parent': each["name"]}, pluck="marsha")
                each["supporting_masha"] = get_supporting_masha
            return {"success": True, "message": get_team_roster_details}
        return {"success": False, "message": "no data found"}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("get_team_roster_details", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}


def create_user_for_team_member(data):
    try:
        get_employee = frappe.get_doc("Employees",data["eid"])
        get_employee.added_as_team_member = 1
        get_employee.save()
        frappe.db.commit()
        if data["current_role_type"] == "Individual Contributor":
            user_creation = create_user(email=get_employee.work_email_address, user_name=get_employee.eid, first_name=get_employee.first_name, last_name=get_employee.last_name,role="Employee")
            if not user_creation["success"]:
                return user_creation
            user_doc = frappe.get_doc("User", get_employee.work_email_address)
            if user_doc:
                b2csuccess = frappe.get_doc('Email Template',"Team Leader Login Details")
                message = b2csuccess.response
                replace_first_name = message.replace("[first_name]", user_doc.first_name)
                replace_email = replace_first_name.replace("[email_id]", user_doc.username)
                send_mail_to_user(content=replace_email, email_id=user_doc.email, subject=b2csuccess.subject)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("create_user_for_team_member", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}
    

@frappe.whitelist()
def check_role_effective_date(job_date=None, job_name=None):
    try:
        # job_date = datetime.datetime.strptime(job_date, "%d-%m-%Y")

        if not job_date and not job_name:
            return {"success": False, "message": "job_date or job_name are mandatory"}
        jobdate = job_date.strftime("%d") +"-"+job_date.strftime("%b")
        current_date = datetime.datetime.now()
        print(type(job_date),  type(datetime.datetime.strptime(f"16-Jun-{current_date.year-1}", "%d-%b-%Y").date()))
        if job_name == "Voyage-AP-Revenue":
            if job_date < datetime.datetime.strptime(f"16-Jun-{current_date.year-1}", "%d-%b-%Y").date():
                return datetime.datetime.strptime(f"01-Jan-{current_date.year}", "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Jun", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Jul", "%d-%b"):
                return datetime.datetime.strptime("01-Jan-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Jul", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Aug", "%d-%b"):
                return datetime.datetime.strptime("01-Feb-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Aug", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Sep", "%d-%b"):
                return datetime.datetime.strptime("01-Mar-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Sep", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Oct", "%d-%b"):
                return datetime.datetime.strptime("01-Apr-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Oct", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Nov", "%d-%b"):
                return datetime.datetime.strptime("01-May-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Nov", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Dec", "%d-%b"):
                return datetime.datetime.strptime("01-Jun-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Dec", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("31-Dec", "%d-%b"):
                return datetime.datetime.strptime("01-Jun-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("01-Jan", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Jan", "%d-%b"):
                return datetime.datetime.strptime("01-Jun-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Jan", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Feb", "%d-%b"):
                return datetime.datetime.strptime("01-Aug-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Feb", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Mar", "%d-%b"):
                return datetime.datetime.strptime("01-Sep-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Mar", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Apr", "%d-%b"):
                return datetime.datetime.strptime("01-Oct-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-Apr", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-May", "%d-%b"):
                return datetime.datetime.strptime("01-Nov-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            elif datetime.datetime.strptime("16-May", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Jun", "%d-%b"):
                return datetime.datetime.strptime("01-Dec-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            else:
                return datetime.datetime.strptime("01-Jan-"+str(current_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
        else:
            if job_date < datetime.datetime.strptime(f"16-Sep-{current_date.year-1}", "%d-%b-%Y").date():
                return datetime.datetime.strptime(f"01-Jan-{current_date.year}", "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Sep", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Oct", "%d-%b"):
                return datetime.datetime.strptime("01-Jan-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Oct", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Nov", "%d-%b"):
                return datetime.datetime.strptime("01-Feb-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Nov", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Dec", "%d-%b"):
                return datetime.datetime.strptime("01-Mar-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Dec", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("31-Dec", "%d-%b"):
                return datetime.datetime.strptime("01-Apr-"+str(job_date.year+1), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("01-Jan", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Jan", "%d-%b"):
                return datetime.datetime.strptime("01-Apr-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Jan", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Feb", "%d-%b"):
                return datetime.datetime.strptime("01-May-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Feb", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Mar", "%d-%b"):
                return datetime.datetime.strptime("01-Jun-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Mar", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Apr", "%d-%b"):
                return datetime.datetime.strptime("01-Jul-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Apr", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-May", "%d-%b"):
                return datetime.datetime.strptime("01-Aug-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-May", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Jun", "%d-%b"):
                return datetime.datetime.strptime("01-Sep-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Jun", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Jul", "%d-%b"):
                return datetime.datetime.strptime("01-Oct-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Jul", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Aug", "%d-%b"):
                return datetime.datetime.strptime("01-Nov-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
            if datetime.datetime.strptime("16-Aug", "%d-%b") <= datetime.datetime.strptime(jobdate, "%d-%b") <= datetime.datetime.strptime("15-Sep", "%d-%b"):
                return datetime.datetime.strptime("01-Dec-"+str(job_date.year), "%d-%b-%Y").strftime("%Y-%m-%d")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("check_role_effective_date", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "message": str(e)}