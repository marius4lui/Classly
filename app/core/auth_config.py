
import os
from typing import List, Optional
from pydantic import BaseModel

class OAuthConfig(BaseModel):
    client_id: str
    client_secret: str
    authorize_url: Optional[str] = None
    access_token_url: Optional[str] = None
    server_metadata_url: Optional[str] = None
    jwks_uri: Optional[str] = None

class LDAPConfig(BaseModel):
    enabled: bool = False
    server: str = "ldap://localhost"
    port: int = 389
    base_dn: str = "dc=example,dc=com"
    bind_dn: str = "cn=admin,dc=example,dc=com"
    bind_password: str = "secret"

class SAMLConfig(BaseModel):
    enabled: bool = False
    entity_id: str = "classly"
    sso_url: str = ""
    cert: str = ""
    key_file: Optional[str] = None
    cert_file: Optional[str] = None

class AuthSettings(BaseModel):
    # OAuth Providers
    google: Optional[OAuthConfig] = None
    microsoft: Optional[OAuthConfig] = None
    github: Optional[OAuthConfig] = None

    # Other methods
    ldap: LDAPConfig = LDAPConfig()
    saml: SAMLConfig = SAMLConfig()

    # 2FA
    enable_2fa: bool = False
    enforce_2fa: bool = False

    # API Keys
    enable_api_keys: bool = False

def get_auth_settings() -> AuthSettings:
    settings = AuthSettings()

    # Google
    if os.getenv("OAUTH_GOOGLE_CLIENT_ID"):
        settings.google = OAuthConfig(
            client_id=os.getenv("OAUTH_GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("OAUTH_GOOGLE_CLIENT_SECRET"),
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
        )

    # Microsoft
    if os.getenv("OAUTH_MICROSOFT_CLIENT_ID"):
        settings.microsoft = OAuthConfig(
            client_id=os.getenv("OAUTH_MICROSOFT_CLIENT_ID"),
            client_secret=os.getenv("OAUTH_MICROSOFT_CLIENT_SECRET"),
            server_metadata_url="https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
        )

    # GitHub
    if os.getenv("OAUTH_GITHUB_CLIENT_ID"):
        settings.github = OAuthConfig(
            client_id=os.getenv("OAUTH_GITHUB_CLIENT_ID"),
            client_secret=os.getenv("OAUTH_GITHUB_CLIENT_SECRET"),
            authorize_url="https://github.com/login/oauth/authorize",
            access_token_url="https://github.com/login/oauth/access_token"
        )

    # LDAP
    settings.ldap.enabled = os.getenv("LDAP_ENABLED", "false").lower() == "true"
    settings.ldap.server = os.getenv("LDAP_SERVER", "ldap://localhost")
    settings.ldap.port = int(os.getenv("LDAP_PORT", "389"))
    settings.ldap.base_dn = os.getenv("LDAP_BASE_DN", "")
    settings.ldap.bind_dn = os.getenv("LDAP_BIND_DN", "")
    settings.ldap.bind_password = os.getenv("LDAP_BIND_PASSWORD", "")

    # SAML
    settings.saml.enabled = os.getenv("SAML_ENABLED", "false").lower() == "true"
    settings.saml.entity_id = os.getenv("SAML_ISSUER", "classly")
    settings.saml.sso_url = os.getenv("SAML_ENTRY_POINT", "")
    settings.saml.cert = os.getenv("SAML_CERT", "")

    # 2FA
    settings.enable_2fa = os.getenv("ENABLE_2FA", "false").lower() == "true"
    settings.enforce_2fa = os.getenv("ENFORCE_2FA", "false").lower() == "true"

    # API Keys
    settings.enable_api_keys = os.getenv("API_KEYS_ENABLED", "false").lower() == "true"

    return settings
