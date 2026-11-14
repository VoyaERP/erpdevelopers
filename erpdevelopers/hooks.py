from . import __version__ as app_version
from erpdevelopers.branding import LOGO_URL, login_stylesheet_url, versioned_public_asset

app_name = "erpdevelopers"
app_title = "ERP Developers"
app_publisher = "ERP Developers"
app_description = "Technology, collaboration, knowledge and intelligent transformation"
app_license = "MIT"
app_version = app_version

# Frappe owns the entire /login DOM, language selector, authentication and 2FA.
# Load scoped, fingerprinted stylesheets before rendering the native form.
# No website JS is injected: no second header, form swap or first-paint flash.
# The homepage loads its own independent brand.css via the Jinja head block.
web_include_css = [login_stylesheet_url(), versioned_public_asset("css/arabic_typography.css")]

# Frappe v16 app tiles and fallback logo resolve the same approved source.
# Hooks apply per installed site; other websites in this Bench are unchanged.
app_logo_url = LOGO_URL

# The site-scoped boot hook changes only the visible ERPNext icon in v16
# app_data (and the legacy Desktop Icons fallback), never permissions/routes.
# Other sites sharing the Bench retain their standard ERPNext logo.
boot_session = "erpdevelopers.desk_branding.brand_erpnext_on_boot"
