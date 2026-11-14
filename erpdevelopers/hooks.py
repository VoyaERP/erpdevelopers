from . import __version__ as app_version
from erpdevelopers.branding import login_stylesheet_url

app_name = "erpdevelopers"
app_title = "ERP Developers"
app_publisher = "ERP Developers"
app_description = "Technology, collaboration, knowledge and intelligent transformation"
app_license = "MIT"
app_version = app_version

# Frappe owns the entire /login DOM, language selector, authentication and 2FA.
# Load the scoped, fingerprinted stylesheet BEFORE rendering the native form.
# No website JS is injected: no second header, form swap or first-paint flash.
# The homepage loads its own independent brand.css via the Jinja head block.
web_include_css = [login_stylesheet_url()]
