
import logging
from ldap3 import Server, Connection, ALL, NTLM
from ldap3.utils.conv import escape_filter_chars
from app.core.auth_config import get_auth_settings

logger = logging.getLogger("uvicorn")
settings = get_auth_settings()

def verify_ldap_credentials(username, password):
    if not settings.ldap.enabled:
        return False

    try:
        server = Server(settings.ldap.server, port=settings.ldap.port, get_info=ALL)

        # Determine Bind DN
        # If username is an email or DN, use it. If it's a simple username, we might need to construct DN.
        # But often we bind with a service account first to search for the user DN.

        # Simple approach: Bind with service account, search for user, then bind with user.
        if settings.ldap.bind_dn and settings.ldap.bind_password:
            conn = Connection(server, user=settings.ldap.bind_dn, password=settings.ldap.bind_password, auto_bind=True)

            safe_username = escape_filter_chars(username)
            search_filter = f"(|(uid={safe_username})(sAMAccountName={safe_username})(mail={safe_username}))"
            conn.search(settings.ldap.base_dn, search_filter, attributes=['dn', 'cn', 'mail'])

            if not conn.entries:
                logger.warning(f"LDAP User not found: {username}")
                return False

            user_dn = conn.entries[0].entry_dn
            user_info = {
                "dn": user_dn,
                "name": str(conn.entries[0].cn) if 'cn' in conn.entries[0] else username,
                "email": str(conn.entries[0].mail) if 'mail' in conn.entries[0] else None
            }
            conn.unbind()

            # Now bind as user
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            conn.unbind()
            return user_info
        else:
            # Direct bind attempt (if we know the pattern)
            # This is harder to guess. Assuming service account is configured for now.
            logger.error("LDAP Bind DN not configured")
            return False

    except Exception as e:
        logger.error(f"LDAP Auth Error: {e}")
        return False

def get_saml_client(request_data):
    """
    Constructs SAML client.
    request_data: dict with 'http_host', 'script_name', 'server_port', 'get_data', 'post_data', 'query_string'
    """
    if not settings.saml.enabled:
        return None

    try:
        from onelogin.saml2.auth import OneLogin_Saml2_Auth
    except ImportError:
        logger.error("pysaml2/python3-saml not installed properly")
        return None

    saml_settings = {
        "strict": True,
        "debug": True,
        "sp": {
            "entityId": settings.saml.entity_id,
            "assertionConsumerService": {
                "url": f"https://{request_data['http_host']}/auth/saml/callback",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": f"https://{request_data['http_host']}/auth/saml/sls",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
        },
        "idp": {
            "entityId": settings.saml.entity_id, # Should be IdP entity ID, but we use what we have
            "singleSignOnService": {
                "url": settings.saml.sso_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": settings.saml.cert
        }
    }

    return OneLogin_Saml2_Auth(request_data, saml_settings)
