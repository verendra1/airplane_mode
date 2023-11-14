from . import __version__ as app_version

app_name = "revenue_management"
app_title = "Revenue Management"
app_publisher = "Caratred Technologies"
app_description = "Revenue Management"
app_email = "info@caratred.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/revenue_management/css/revenue_management.css"
# app_include_js = "/assets/revenue_management/js/revenue_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/revenue_management/css/revenue_management.css"
# web_include_js = "/assets/revenue_management/js/revenue_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "revenue_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "revenue_management.utils.jinja_methods",
#	"filters": "revenue_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "revenue_management.install.before_install"
# after_install = "revenue_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "revenue_management.uninstall.before_uninstall"
# after_uninstall = "revenue_management.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "revenue_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
    "RMRS Deployment": {
        "before_insert": "revenue_management.revenue_management.doctype.rmrs_deployment.rmrs_deployment.update_name_field"
    },
    "Team Leaders": {
        "after_insert": "revenue_management.revenue_management.doctype.team_leaders.team_leaders.create_team_leader_as_user"
    },
    "Approvers" : {
        "after_insert": "revenue_management.revenue_management.doctype.approvers.approvers.create_approver_as_user"
    }

}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"revenue_management.tasks.all"
#	],
#	"daily": [
#		"revenue_management.tasks.daily"
#	],
#	"hourly": [
#		"revenue_management.tasks.hourly"
#	],
#	"weekly": [
#		"revenue_management.tasks.weekly"
#	],
#	"monthly": [
#		"revenue_management.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "revenue_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "revenue_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "revenue_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["revenue_management.utils.before_request"]
# after_request = ["revenue_management.utils.after_request"]

# Job Events
# ----------
# before_job = ["revenue_management.utils.before_job"]
# after_job = ["revenue_management.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"revenue_management.auth.validate"
# ]
