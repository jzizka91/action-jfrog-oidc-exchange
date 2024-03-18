import json
import base64
import os
import sys
import id
import requests
import re

# Rendered if OIDC identity token retrieval fails for any reason.
TOKEN_RETRIEVAL_FAILED_MESSAGE = """
OpenID Connect token retrieval failed: {identity_error}

This generally indicates a workflow configuration error, such as insufficient
permissions. Make sure that your workflow has `id-token: write` configured
at the job level, e.g.:

```yam
permissions:
  id-token: write
```

Learn more at https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings.
"""

# # Rendered if the token exchange fails due to unsuccessful id_token verification.
TOKEN_RESPONSE_VEVERIFICATION_FAILED = """
Token exchange failed: verification produced {status_code} response.

This strongly suggests JFrog Access failed to validate claims in the ID_Token. Make sure Jfrog's Identity Mappings is configurated correctly.
"""

# Rendered if integrity validation of Json token has failed.
TOKEN_INTEGRITY_VALIDATION_FAILED = """
Token integrity validation failed: Decoding the token wasn't successful. An unexpected
{status_code} response was produced.

This strongly suggests a server configuration or downtime issue; wait
a few minutes and try again.
"""

def get_normalized_input(name: str):
    name = f"INPUT_{name.upper()}"
    return os.getenv(name)

def debug(msg: str):
    print(f"::debug::{msg.title()}", file=sys.stderr)

jfrog_oidc_audience = get_normalized_input("audiance")
jfrog_oidc_integration = get_normalized_input("integration")
jfrog_token_exchange_url = f"https://datamole.jfrog.io/access/api/v1/oidc/token"

debug(f"selected exchange endpoint: {jfrog_token_exchange_url}")

# Request GitHub's ID Token
try:
    github_id_token = id.detect_credential(audience=jfrog_oidc_audience)
except id.IdentityError as identity_error:
    exit(
        TOKEN_RETRIEVAL_FAILED_MESSAGE.format(
            identity_error = identity_error
        ),
    )

# Do token exchange to get Jfrog's access token
try:
    token_resp = requests.post(
        jfrog_token_exchange_url,
        json={"grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
            "subject_token": github_id_token,
            "provider_name": jfrog_oidc_integration
        },
    )
    token_resp.raise_for_status()
except requests.HTTPError as http_error:
    if http_error.response.status_code == 403:
        exit(
            TOKEN_RESPONSE_VEVERIFICATION_FAILED.format(
                status_code=http_error)
        )

# Verify token integrity
try:
    token_full = token_resp.json()
except requests.JSONDecodeError:
    exit(
        TOKEN_INTEGRITY_VALIDATION_FAILED.format(
            status_code=token_resp.status_code,
        ),
    )

# Split the token parts by dot and get the middle payload part
token_payload = str(token_full).split(".")[1]

# Payload is base64 encoded, decode it and get a plain string
# To make sure decoding will always work - max padding ("==") is added
# If max padding is not needed, it is ignored
token_payload_decoded = str(base64.b64decode(token_payload + "=="), "utf-8")

# Load Json payload to dict for easy access
payload = json.loads(token_payload_decoded)

# Access token's "sub" element that contains Jfrog's user information
payload_subject = payload["sub"]

# Extract username from token's "sub" element 
payload_subject_user = re.sub(".*" + 'users/', '', payload_subject)

# Mask the token, so it won't accidentally get leaked in logs
print(f"::add-mask::{token_full}", file=sys.stderr)

# Make jfrog_auth_credentials available for publishing
github_env_file = os.getenv("GITHUB_ENV")

with open(github_env_file, "a") as file:
    file.write(f"JFROG_SERVICE_USERNAME={payload_subject_user}\n")
    file.write(f"JFROG_SERVICE_JWT={token_full}")
