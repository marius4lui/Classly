from fastapi.templating import Jinja2Templates
from app.core.config import settings

templates = Jinja2Templates(directory="app/templates")

# Inject feature flags into templates
templates.env.globals["feature_flags"] = settings
templates.env.globals["gtm_id"] = settings.GTM_ID
