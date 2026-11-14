from . import __version__ as app_version

app_name = "erpdevelopers"
app_title = "ERP Developers"
app_publisher = "ERP Developers"
app_description = "Technology, collaboration, knowledge and intelligent transformation"
app_license = "MIT"
app_version = app_version

# Frappe owns /login, 2FA, password reset, social login and sessions.
# The homepage loads brand.css explicitly from its head_include block.
# Avoid loading it globally or twice; login.css only styles /login.
# Frappe's native template and auth handling remain unchanged.
web_include_css = ["/assets/erpdevelopers/css/login.css"]
web_include_js = ["/assets/erpdevelopers/js/login_chrome.js"]
