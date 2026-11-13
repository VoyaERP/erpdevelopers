from . import __version__ as app_version

app_name = "erpdevelopers"
app_title = "ERP Developers"
app_publisher = "ERP Developers"
app_description = "Technology, collaboration, knowledge and intelligent transformation"
app_license = "MIT"
app_version = app_version

# Frappe owns /login, 2FA, password reset, social login and sessions.
# Website assets are loaded by Frappe's native website template only.
# The login script and login stylesheet are strictly scoped to /login.
web_include_css = [
    "/assets/erpdevelopers/css/brand.css",
    "/assets/erpdevelopers/css/login.css",
]
web_include_js = ["/assets/erpdevelopers/js/login_chrome.js"]
