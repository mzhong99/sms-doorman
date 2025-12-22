import os
import uvicorn

def main() -> None:
    # Allow env overrides; keep sane defaults.
    host = os.getenv("SMS_DOORMAN_HOST", "127.0.0.1")
    port = int(os.getenv("SMS_DOORMAN_PORT", "8000"))
    log_level = os.getenv("SMS_DOORMAN_LOG_LEVEL", "info")

    # IMPORTANT: pass the import string, not the app object.
    # This keeps uvicorn reload/workers behavior compatible if you ever use them.
    uvicorn.run("sms_doorman.application:app", host=host, port=port, log_level=log_level)

if __name__ == "__main__":
    main()
