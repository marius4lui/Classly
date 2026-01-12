
from authlib.integrations.starlette_client import OAuth
from app.core.auth_config import get_auth_settings

oauth = OAuth()
settings = get_auth_settings()

def register_oauth_providers():
    if settings.google:
        oauth.register(
            name='google',
            client_id=settings.google.client_id,
            client_secret=settings.google.client_secret,
            server_metadata_url=settings.google.server_metadata_url,
            client_kwargs={
                'scope': 'openid email profile'
            }
        )

    if settings.microsoft:
        oauth.register(
            name='microsoft',
            client_id=settings.microsoft.client_id,
            client_secret=settings.microsoft.client_secret,
            server_metadata_url=settings.microsoft.server_metadata_url,
            client_kwargs={
                'scope': 'openid email profile User.Read'
            }
        )

    if settings.github:
        oauth.register(
            name='github',
            client_id=settings.github.client_id,
            client_secret=settings.github.client_secret,
            authorize_url=settings.github.authorize_url,
            access_token_url=settings.github.access_token_url,
            client_kwargs={
                'scope': 'user:email'
            }
        )

register_oauth_providers()
