from services.license.license_validator import (
    decode_request_code,
    encode_request_code,
    is_license_expired,
    parse_license_blob,
    verify_license_signature,
)


def verify_license_blob(license_blob: str, public_key_pem: str):
    data = parse_license_blob(license_blob)
    verify_license_signature(data, public_key_pem)
    return data


__all__ = [
    "encode_request_code",
    "decode_request_code",
    "verify_license_blob",
    "verify_license_signature",
    "is_license_expired",
]
