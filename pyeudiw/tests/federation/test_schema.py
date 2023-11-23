
from pyeudiw.tools.utils import iat_now, exp_from_now
from pyeudiw.federation import is_es, is_ec

NOW = iat_now()
EXP = exp_from_now(5)

ta_es = {
    "exp": EXP,
    "iat": NOW,
    "iss": "https://trust-anchor.example.eu",
    "sub": "https://intermediate.eidas.example.org",
    'jwks': {"keys": []},
    "source_endpoint": "https://rp.example.it"
}

ta_ec = {
    "exp": EXP,
    "iat": NOW,
    'iss': 'https://registry.eidas.trust-anchor.example.eu/',
    'sub': 'https://registry.eidas.trust-anchor.example.eu/',
    'jwks': {"keys": []},
    'metadata': {
            'wallet_relying_party': {
                "application_type": "web",
                "client_id": "https://rp.example.it",
                "client_name": "Name of an example organization",
                "jwks": {
                    "keys": [
                        {
                            "kty": "RSA",
                            "use": "sig",
                            "n": "1Ta-sE …",
                            "e": "AQAB",
                            "kid": "YhNFS3YnC9tjiCaivhWLVUJ3AxwGGz_98uRFaqMEEs",
                            "x5c": ["..."]
                        }
                    ]
                },
                'contacts': [],
                'request_uris': [],
                'redirect_uris': [],
                'default_acr_values': [],
                'presentation_definitions': [],
                'authorization_signed_response_alg': ['RS256'],
                'authorization_encrypted_response_alg': ["RSA-OAEP"],
                'authorization_encrypted_response_enc': ["A128CBC-HS256"],
                'subject_type': '',
                'require_auth_time': True,
                'id_token_encrypted_response_alg': ["RSA-OAEP"],
                'id_token_encrypted_response_enc': ["A128CBC-HS256"],
                'id_token_signed_response_alg': ["ES256"],
                'default_max_age': 5000,
                'vp_formats': {
                    'jwt_vp_json': {
                        'alg': ["EdDSA"]
                    }
                },
                'policy_uri': ''
            },
            'federation_entity': {
                'organization_name': 'example TA',
                'contacts': ['tech@eidas.trust-anchor.example.eu'],
                'homepage_uri': 'https://registry.eidas.trust-anchor.example.eu/',
                'logo_uri': 'https://registry.eidas.trust-anchor.example.eu/static/svg/logo.svg',
                'policy_uri': 'https://registry.eidas.trust-anchor.example.eu/policy/',
                'federation_fetch_endpoint': 'https://registry.eidas.trust-anchor.example.eu/fetch/',
                'federation_resolve_endpoint': 'https://registry.eidas.trust-anchor.example.eu/resolve/',
                'federation_list_endpoint': 'https://registry.eidas.trust-anchor.example.eu/list/',
                'federation_trust_mark_status_endpoint': 'https://registry.eidas.trust-anchor.example.eu/trust_mark_status/',
            },
            'authority_hints': []
        },
    'trust_marks_issuers': {
        'https://registry.eidas.trust-anchor.example.eu/openid_relying_party/public/': [
            'https://registry.spid.eidas.trust-anchor.example.eu/',
            'https://public.intermediary.spid.org/'
        ],
        'https://registry.eidas.trust-anchor.example.eu/openid_relying_party/private/': [
            'https://registry.spid.eidas.trust-anchor.example.eu/',
            'https://private.other.intermediary.org/'
        ]
    },
    'constraints': {'max_path_length': 1},
    'authority_hints': [],
}


def test_is_es():
    assert is_es(ta_es)


def test_is_es_false():
    assert not is_es(ta_ec)


def test_is_ec():
    assert is_ec(ta_ec)


def test_is_ec_false():
    assert not is_ec(ta_es)
