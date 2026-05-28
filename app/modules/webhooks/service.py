import json

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import ValidationError
from app.modules.payment_events.models import PaymentEvent
from app.modules.payment_events.service import PaymentEventService
from app.modules.providers.signatures import verify_fake_provider_signature
from app.modules.webhooks.schemas import FakeProviderWebhookPayload


class WebhookIngestionResult:
    def __init__(
        self,
        *,
        payment_event: PaymentEvent,
        is_duplicate: bool,
    ) -> None:
        self.payment_event = payment_event
        self.is_duplicate = is_duplicate


class WebhookService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()
        self.payment_events = PaymentEventService(db)

    def ingest_fake_provider_webhook(
        self,
        *,
        raw_body: bytes,
        signature_header: str | None,
    ) -> WebhookIngestionResult:
        verify_fake_provider_signature(
            raw_body=raw_body,
            signature_header=signature_header,
            secret=self.settings.fake_provider_webhook_secret,
            tolerance_seconds=self.settings.webhook_signature_tolerance_seconds,
        )

        payload_dict = self._parse_json(raw_body)
        payload = self._validate_payload(payload_dict)

        result = self.payment_events.ingest_event(
            provider_name="fake_provider",
            provider_event_id=payload.provider_event_id,
            event_type=payload.event_type,
            payload=payload.model_dump(),
        )

        return WebhookIngestionResult(
            payment_event=result.payment_event,
            is_duplicate=result.is_duplicate,
        )

    def _parse_json(self, raw_body: bytes) -> dict:
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValidationError("Invalid JSON payload.") from exc

    def _validate_payload(
        self,
        payload_dict: dict,
    ) -> FakeProviderWebhookPayload:
        try:
            return FakeProviderWebhookPayload(**payload_dict)
        except PydanticValidationError as exc:
            raise ValidationError("Invalid webhook payload.") from exc