import re
import requests
import urllib.parse

from pyeudiw.jwt.utils import decode_jwt_payload

from commons import (
    ISSUER_CONF,
    setup_test_db_engine,
    apply_trust_settings,
    create_saml_auth_request,
    create_authorize_response,
    create_holder_test_data,
    create_issuer_test_data,
    extract_saml_attributes
)
from settings import TIMEOUT_S

# put a trust attestation related itself into the storage
# this is then used as trust_chain header parameter in the signed request object
db_engine_inst = setup_test_db_engine()
db_engine_inst = apply_trust_settings(db_engine_inst)

def _extract_request_uri(e: requests.exceptions.InvalidSchema) -> str:
    request_uri = re.search(r'request_uri=(.*?)(?:\'|$)', urllib.parse.unquote_plus(e.args[0])).group(1)
    return request_uri


# initialize the user-agent
http_user_agent = requests.Session()

auth_req_url = create_saml_auth_request()
headers_mobile = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1"
}
request_uri = ""

try:
    authn_response = http_user_agent.get(
        url=auth_req_url,
        verify=False,
        headers=headers_mobile,
        timeout=TIMEOUT_S
    )
except requests.exceptions.InvalidSchema as e:
    request_uri = _extract_request_uri(e)

sign_request_obj = http_user_agent.get(
    request_uri,
    verify=False,
    timeout=TIMEOUT_S)

request_object_claims = decode_jwt_payload(sign_request_obj.text)
response_uri = request_object_claims["response_uri"]

# Provide an authentication response
verifiable_credential = create_issuer_test_data()
verifiable_presentations = create_holder_test_data(
    verifiable_credential,
    request_object_claims["nonce"],
    request_object_claims["client_id"]
)
wallet_response_data = create_authorize_response(
    verifiable_presentations,
    request_object_claims["state"],
    response_uri
)

authz_response = http_user_agent.post(
    response_uri,
    verify=False,
    data={"response": wallet_response_data},
    timeout=TIMEOUT_S
)

assert authz_response.status_code == 200
assert authz_response.json().get("redirect_uri", None) is not None

callback_uri = authz_response.json().get("redirect_uri", None)
satosa_authn_response = http_user_agent.get(
    callback_uri,
    verify=False,
    timeout=TIMEOUT_S
)

assert "SAMLResponse" in satosa_authn_response.content.decode()
print(satosa_authn_response.content.decode())

attributes = extract_saml_attributes(satosa_authn_response.content.decode())
# expect to have a non-empty list of attributes
assert attributes

expected = {
    # https://oidref.com/2.5.4.42
    "urn:oid:2.5.4.42": ISSUER_CONF["sd_specification"].split("!sd given_name:")[1].split('"')[1].lower(),
    # https://oidref.com/2.5.4.4
    "urn:oid:2.5.4.4": ISSUER_CONF["sd_specification"].split("!sd family_name:")[1].split('"')[1].lower()
}

for exp_att_name, exp_att_value in expected.items():
    result_index = -1
    for i, attribute in enumerate(attributes):
        if attribute["name"] == exp_att_name:
            result_index = i
            break
    assert result_index != -1, f"missing attribute with name=[{exp_att_name}] in result set"
    obt_att_value = attributes[result_index].contents[0].contents[0]
    assert exp_att_value == obt_att_value, f"wrong attrirbute parsing expected {exp_att_value}, obtained {obt_att_value}"


print("TEST PASSED")