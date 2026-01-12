import os
from fastapi.templating import Jinja2Templates

# Initialize templates once
templates = Jinja2Templates(directory="app/templates")

# Load configuration from environment variables
APP_NAME = os.getenv("APP_NAME", "Classly")
APP_LOGO_URL = os.getenv("APP_LOGO_URL", None)
APP_FAVICON_URL = os.getenv("APP_FAVICON_URL", "/static/favicon.ico")
PRIMARY_COLOR = os.getenv("PRIMARY_COLOR", None)
SECONDARY_COLOR = os.getenv("SECONDARY_COLOR", None)
DEFAULT_THEME = os.getenv("DEFAULT_THEME", "light")
ALLOW_USER_THEME_TOGGLE = os.getenv("ALLOW_USER_THEME_TOGGLE", "true").lower() == "true"
GTM_ID = os.getenv("GTM_ID")
IMPRESSUM_NAME = os.getenv("IMPRESSUM_NAME", "Nicht konfiguriert")
IMPRESSUM_STREET = os.getenv("IMPRESSUM_STREET", "Nicht konfiguriert")
IMPRESSUM_PLZ_ORT = os.getenv("IMPRESSUM_PLZ_ORT", "Nicht konfiguriert")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "Nicht konfiguriert")

# Set globals
templates.env.globals["app_name"] = APP_NAME
templates.env.globals["app_logo_url"] = APP_LOGO_URL
templates.env.globals["app_favicon_url"] = APP_FAVICON_URL
templates.env.globals["primary_color"] = PRIMARY_COLOR
templates.env.globals["secondary_color"] = SECONDARY_COLOR
templates.env.globals["default_theme"] = DEFAULT_THEME
templates.env.globals["allow_user_theme_toggle"] = ALLOW_USER_THEME_TOGGLE
templates.env.globals["gtm_id"] = GTM_ID

# Legal info globals (so we don't need to pass them in every view if we use them in base/footer)
templates.env.globals["legal_info"] = {
    "name": IMPRESSUM_NAME,
    "street": IMPRESSUM_STREET,
    "plz_ort": IMPRESSUM_PLZ_ORT,
    "email": CONTACT_EMAIL
}
