class ProviderError(Exception):
    """Base error for payment provider failures."""


class ProviderTemporaryError(ProviderError):
    """Retryable provider error, such as timeout or temporary 5xx."""


class ProviderPermanentError(ProviderError):
    """Non-retryable provider error, such as invalid request."""