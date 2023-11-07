from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding
from datetime import datetime, timedelta, date
from pyeudiw.x509.verify import verify_x509_cert_chain

def gen_chain(date: datetime) -> dict[str, list[bytes] | datetime]:
    # Generate a private key for the CA
    ca_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Generate a private key for the intermediate
    intermediate_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Generate a private key for the leaf
    leaf_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Generate the CA's certificate
    ca = x509.CertificateBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"ca.example.com"),
    ])).issuer_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"ca.example.com"),
    ])).public_key(
        ca_private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=1), critical=True,
    ).sign(ca_private_key, hashes.SHA256())

    # Generate the intermediate's certificate
    intermediate = x509.CertificateBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"intermediate.example.net"),
    ])).issuer_name(ca.subject).public_key(
        intermediate_private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=0), critical=True,
    ).sign(ca_private_key, hashes.SHA256())

    # Generate the leaf's certificate
    leaf = x509.CertificateBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"leaf.example.org"),
    ])).issuer_name(intermediate.subject).public_key(
        leaf_private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    ).sign(intermediate_private_key, hashes.SHA256())

    # Here the certificate chain in DER format, then encoded in base64 to use it according to RFC 9360:

    # Create a certificate chain
    certificate_chain = [
        ca.public_bytes(Encoding.DER),
        intermediate.public_bytes(Encoding.DER),
        leaf.public_bytes(Encoding.DER)
    ]

    return {
        "exp": date,
        "x5c": certificate_chain
    }


def test_valid_chain():
    chain = gen_chain(datetime.fromisoformat('2050-12-04'))
    assert verify_x509_cert_chain(chain) == True

def test_valid_chain_invalid_date():
    chain = gen_chain(datetime.fromisoformat('2014-12-04'))
    assert verify_x509_cert_chain(chain) == False

def test_invalid_intermediary_chain():
    chain = gen_chain(datetime.fromisoformat('2050-12-04'))
    chain["x5c"][1] = b'0\x82\x02\xe00\x82\x01\xc8\xa0\x03\x02\x01\x02\x02\x14c\xef!\x17\xde\x88(\xbf\xb1\xdc\xad\x17\xc2`\xad\x15S\x95\n\xb60\r\x06\t*\x86H\x86\xf7\r\x01\x01\x0b\x05\x000\x191\x170\x15\x06\x03U\x04\x03\x0c\x0eca.example.com0\x1e\x17\r231107165050Z\x17\r241106165050Z0#1!0\x1f\x06\x03U\x04\x03\x0c\x18intermediate.example.net0\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\x916\xde\x9b\x0b\xeb\xd4\x91\xder\x1c\x9b\x0b\x06s\xb3W\x08\xa1\x12\x19K\x05\xf9\x87\xf3Uk\x15\xfeQ\xf2#\x103\x9e6\x04]s\x87\x13cD\x9d\xed3\xd7\x1bg\xd6#Tau\x03[\xc8H\t\x9e\xd7H\xae\xd5\x85i8W\xf3\x0f\xf4\xab\xa3\xc6G\x95\xb9\xc2\x19\xb0\x07\x98#\xde\xa8\xa6\xb2&\x95\xc3\x7f\xb0\x10b3\xaa\xd2QlAV`M\x7fhgI]Y\xdaD\xe7[\xdb\x87\xf1\x07\x01D\xbf\xe7\x89\xac7\xe00\x141U\xff\xe6r\xa1>\xfb5q\x18{V:\xc7\xb1$B\xfb\xc2@\xa7u\x18\x87\x1d\xe26\x17\xdc\xf8\xb5\xe2\x88c\xa2t\xa5[\x06\x1f\xc1k\x80\x9c9s\xb9\x94\x85\x00^\xbf\xcc!w\xbf\xee]PW\xc8[\xdc3\xfb\xa58V0n\xebV\xf3\xad\xa2\xf0\xec\x96\x1d\xc0\xe3Q7\xd8pH\x11\xda\xfc\xdds\xb1\xff\x87X?d\xe8j\xb6\x12A_\r\xd8\x17\xcdt\x97\xedS\x99\xb8\xeaJ/4\xc2\xfd\xe8v>\xd9`\xed\x02K\x02\x03\x01\x00\x01\xa3\x160\x140\x12\x06\x03U\x1d\x13\x01\x01\xff\x04\x080\x06\x01\x01\xff\x02\x01\x000\r\x06\t*\x86H\x86\xf7\r\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x00\xaek\x9d\x9fx\x02\x99Rt\xf1x\xd2\xc3Y\x1c\xacB\x95\xdb\xe3\xf6\x98\xbah\xae\xd6$\xfcDs\xfaO\x1e\xec\xf2\x83@\xbf\xc6\x0f\x8a\xf2\xe8\x98\x18S\xa2\xb2\xfcXZ]\x01\xccX\xb3F$\xe0\x8dn\x11\x83\x92\xe6\x1d\x96NMDO6L:\xc4\xc5=%Q4\xd4\xca\xfct\xd1(6\xf1\xade~Or\xe0AM8\xbb0y=\xdc~D\x06g\x07p\x1c\x9eu)K~\xb0M\x81\xa5gfS\xfaG\xafW\x05N\xa0\x0f\x9a\xc9=\x06\xf7\xdb_\r\xc1\xf1\x1d\xea\xb0\x85\xf8p\x1e\xa5\xb0\xb6\xact\xb1\x86UmVNX\xb6\x8c\x07o\xc6\x0e\x88\xe7,\x9e\xbe\xb6w\xf9\x88\xca!\xb2k\xcdE\xaf%r\xfd\x1d+\xab\x1do/i\x84~\xad\xa1\x99\x80\x03\xf4\xf2s\x88\x90\xa3\x93\x83&\x1b\xa1a\xc9\xe6\\\xfe\xcar\x17\x83\x84\x8bB\x8e\x8d\xcb\xb2\x1bD\x08\xb5\x11y\xad\xa6~\x9ae5\xa4\x88\xac\xae\x03\xe9\xb2&\x05\x149\xa0\x86I\x84\xc1`!F\xb8'
    assert verify_x509_cert_chain(chain) == False

def test_invalid_len():
    chain = gen_chain(datetime.fromisoformat('2014-12-04'))
    del chain["x5c"][0]
    del chain["x5c"][1]
    assert verify_x509_cert_chain(chain) == False

def test_invalid_chain_order():
    chain = gen_chain(datetime.fromisoformat('2014-12-04'))
    chain["x5c"].reverse()
    assert verify_x509_cert_chain(chain) == False