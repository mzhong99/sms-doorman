import logging

from fastapi import FastAPI, Request, Response, HTTPException
from sms_doorman.server import TwilioExecServer

_logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI()
server = TwilioExecServer()

@app.post("/twillio/sms")
async def twilio_sms(request: Request):
    form = dict(await(request.form()))
    xml = server.handle_sms(
        path=request.url.path,
        query=request.url.query,
        headers=request.headers,
        form=form,
    )

    return Response(content=xml, media_type="application/xml")
