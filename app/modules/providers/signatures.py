import hashlib
import hmac
import time

from app.core.errors import UnauthorizedError, ValidationError


SIGNATURE_SCHEME = "v1"


def generate_fake_provider_signature(
    *,
    raw_body: bytes,
    secret: str,
    timestamp: int | None = None,
) -> str:
    timestamp = timestamp or int(time.time())

    signed_payload = f"{timestamp}.".encode("utf-8") + raw_body

    signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=signed_payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return f"t={timestamp},{SIGNATURE_SCHEME}={signature}"


def verify_fake_provider_signature(
    *,
    raw_body: bytes,
    signature_header: str | None,
    secret: str,
    tolerance_seconds: int,
) -> None:
    if not signature_header:
        raise UnauthorizedError("Missing provider signature.")

    timestamp, received_signature = _parse_signature_header(signature_header)

    now = int(time.time())

    if abs(now - timestamp) > tolerance_seconds:
        raise UnauthorizedError("Provider signature timestamp is outside tolerance.")

    expected_header = generate_fake_provider_signature(
        raw_body=raw_body,
        secret=secret,
        timestamp=timestamp,
    )

    _, expected_signature = _parse_signature_header(expected_header)

    if not hmac.compare_digest(expected_signature, received_signature):
        raise UnauthorizedError("Invalid provider signature.")


def _parse_signature_header(signature_header: str) -> tuple[int, str]:
    try:
        parts = signature_header.split(",")

        values = {}

        for part in parts:
            key, value = part.split("=", 1)
            values[key] = value

        timestamp = int(values["t"])
        signature = values[SIGNATURE_SCHEME]

        return timestamp, signature

    except (KeyError, ValueError) as exc:
        raise ValidationError("Invalid provider signature format.") from exc