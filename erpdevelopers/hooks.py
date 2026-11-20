from . import __version__ as app_version
from erpdevelopers.branding import LOGO_URL, login_stylesheet_url, versioned_public_asset

app_name = "erpdevelopers"
app_title = "ERP Developers"
app_publisher = "ERP Developers"
app_description = "Technology, collaboration, knowledge and intelligent transformation"
app_license = "MIT"
app_version = app_version

# Retain native Frappe login and authentication. Website branding is site-scoped.
web_include_css = [login_stylesheet_url()]
web_include_css.append(versioned_public_asset("css/arabic_typography.css"))
app_logo_url = LOGO_URL

# Frappe 16 app_data / Desktop Icons boot payload customization is deliberately
# not registered on the Frappe 15 branch. Validate v15 Desk branding separately.
# Login context override also requires v15 integration verification before enabling.
