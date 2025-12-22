import time
import os

import logging

from twilio.twiml.messaging_response import MessagingResponse

_logger = logging.getLogger(__name__)

RATE_LIMIT_SEC = 0.5

class TwilioExecServer:
    def __init__(self):
        self.sms_callbacks: list[callable[str, str]] = []

    def _enforce_rate_limit(self, caller: str) -> None:
        last_sec = self.last_sms_rx.get(caller, 0.0)
        now_sec = time.time()
        if now_sec - last_sec < RATE_LIMIT_SEC:
            raise RuntimeError(f"Caller {caller} was rate limited")
        self.last_sms_rx[caller] = now_sec

    def handle_sms(self, *, path: str, query: str, headers: Mapping[str, str], form: Mapping[str, str]) -> str:
        caller = form.get("From", "")
        body = (form.get("Body", "") or "").strip()

        _logger.info(f"GOT: {caller} - {body}")
        for callback in self.sms_callbacks:
            callback(caller, body)

        resp = MessagingResponse()
        resp.message("OK")

        return str(resp)

    def add_callback(self, callback):
        self.sms_callbacks.append(callback)
