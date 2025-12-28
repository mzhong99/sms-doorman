import os
import logging

from fastapi import FastAPI, Request, Response, HTTPException
from sms_doorman.server import TwilioExecServer
from sms_doorman.door_controller import DoorController, VirtualDoorController
from pathlib import Path

_logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def is_raspberry_pi() -> bool:
    forceflag = os.getenv("SMS_DOORMAN_IS_RPI", "")
    if forceflag == "1":
        return True
    if forceflag == "0":
        return True

    model = Path("/proc/device-tree/model")
    if not model.exists():
        return False

    try:
        return "raspberry pi" in model.read_text().lower()
    except OSError:
        return False

def service_sms_text(caller: str, sms_content: str):
    _logger.info("Received text '{content}' from '{caller}'")
    door.actuate(3.0)

app = FastAPI()
server = TwilioExecServer()
door = VirtualDoorController()

if is_raspberry_pi():
    door = DoorController()
    _logger.info("Raspberry Pi GPIO interop enabled.")

server.add_callback(service_sms_text)

@app.post("/twilio/sms")
async def twilio_sms(request: Request):
    form = dict(await(request.form()))
    xml = server.handle_sms(
        path=request.url.path,
        query=request.url.query,
        headers=request.headers,
        form=form,
    )

    return Response(content=xml, media_type="application/xml")
