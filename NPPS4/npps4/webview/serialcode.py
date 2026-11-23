import urllib.parse
import os

import fastapi
import pydantic
from ..apworld import ap_client
from archipelagopy import packets, structs
import asyncio
import json

from .. import data
from .. import idol
from .. import serialcode
from .. import util
from ..app import app
from ..system import user
from ..config import config

from typing import Annotated


class SerialCodeAPIRequest(pydantic.BaseModel):
    key1: str
    key2: str
    key3: str
    key4: str


class SerialCodeAPIResponse(pydantic.BaseModel):
    ok: bool
    msg: str


@app.webview.get("/serialCode/index")
async def serial_code_index(request: fastapi.Request):
    token = ""
    authorize_header = request.headers.get("Authorize")
    if authorize_header is not None:
        token = util.extract_token_from_authorize(authorize_header)

    return app.templates.TemplateResponse(
        request, "ap_connect.html", {"token": token, "lang": request.headers.get("lang", "en")}
    )


@app.webview.post(
    "/serialCode/index", response_class=fastapi.responses.JSONResponse, response_model=SerialCodeAPIResponse
)
async def serial_code_index_post(
    authorize: Annotated[str, fastapi.Header()],
    lang: Annotated[idol.Language, fastapi.Header(alias="LANG")],
    key_request: SerialCodeAPIRequest,
):
    try:
        async with idol.BasicSchoolIdolContext(lang) as context:
            token = util.extract_token_from_authorize(authorize)
            if token is None:
                return SerialCodeAPIResponse(ok=False, msg="Missing Token")

            current_user = await user.get_from_token(context, token)
            if current_user is None:
                return SerialCodeAPIResponse(ok=False, msg="Missing User")
            
            ap_client.linked_user = current_user
            ap_client.ap_context = context
            ap_client.user_id = current_user.id
            #save_data = json.load(open(os.path.join(config.ROOT_DIR, "data\\ap_save.json"), "r"))
            #ap_client.save_data = save_data
            #if not ap_client.save_data["user_id"] == current_user.id:
                #await user.delete_user(context, current_user.id)
            server_address = key_request.key1.strip()
            server_port = key_request.key2.strip()
            slot_name = key_request.key3.strip()
            password = key_request.key4.strip()
            await ap_client.connect_to_server(server_address,server_port,slot_name,password)
            result = await ap_client.get_errors()
            return SerialCodeAPIResponse(ok=result["ok"], msg=result["msg"])
        
    except Exception as e:
        util.log("Error while running serial code", severity=util.logging.ERROR, e=e)
        return SerialCodeAPIResponse(ok=False, msg=f"Connection Error: {str(e)}")
