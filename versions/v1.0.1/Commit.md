fix(security): harden oauth, csrf, cookies, cors, headers and xss handling

- add CSRF middleware and helper (`app/core/csrf.py`) with double-submit token pattern
- add frontend CSRF propagation for forms, HTMX and fetch requests
- harden OAuth authorize/token flow with strict client and redirect validation
- enforce/validate OAuth client secret via env-based control
- switch logout flow to `POST /auth/logout` (legacy GET optionally disabled)
- make secure cookie behavior env-driven (`COOKIE_SECURE`)
- replace wildcard CORS with explicit allowlist (`CORS_ALLOW_ORIGINS`)
- add secure response headers (CSP, XFO, XCTO, Referrer-Policy, optional HSTS)
- stop leaking session token via domain migration redirect query strings
- remove internal exception detail leakage in admin backup endpoint
- protect public feed endpoints with token requirement option
- sanitize event detail rendering paths in frontend scripts to mitigate stored XSS

Tag command after commit:

git tag -a v1.0.1 -m "v1.0.1" HEAD
