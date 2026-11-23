import fastapi.responses
import os

from .. import util
from ..app import app
from ..apworld import ap_client
from ..config import config


@app.webview.get("/announce/index")
def announce_index():
    util.stub("announce", "index")
    if not ap_client.is_connected:
        with open(os.path.join(config.ROOT_DIR, "maintenance.txt"), "w") as maintenance:
            maintenance.write("Disconnected from APWorld. Please Reconnect.")
        return fastapi.responses.RedirectResponse("/webview.php/serialCode/index", 302)
    else:
        if ap_client.initialized:
            ap_client.initialized = False
            with open(os.path.join(config.ROOT_DIR, "maintenance.txt"), "w") as maintenance:
                maintenance.write("Disconnected from APWorld. Please Reconnect.")
            return fastapi.responses.RedirectResponse("/webview.php/apworld/refresh", 302)
        else:
            ap_client.initialized = True
            return fastapi.responses.RedirectResponse("/webview.php/apworld/connected", 302)

@app.webview.get("/apworld/refresh")
def apworld_index(request: fastapi.Request):
    return app.templates.TemplateResponse(
        request, "ap_refresh.html"
    )

@app.webview.get("/apworld/connected")
async def apworld_index(request: fastapi.Request):
    #await ap_client.login_sync()
    return app.templates.TemplateResponse(
        request, "ap_connected.html"
    )

@app.webview.get("/apworld/tracker")
async def apworld_index(request: fastapi.Request):
    if ap_client.is_connected:
        return app.templates.TemplateResponse(
            request,
            "ap_tracker.html",
            {
                "is_connected": ap_client.is_connected,
                "options": ap_client.get_tracker_options(),
                "available_checks" : ap_client.get_available_checks(),
                "slot_name": ap_client.slot_name,
                "completion": await ap_client.check_completion(),
                "completion_percent": int((await ap_client.check_completion() / ap_client.options["live_count"])*100),
                "story_chapters": ap_client.get_tracker_stories()
            }
        )
    else:
        return app.templates.TemplateResponse(
            request, "ap_tracker_disconnected.html"
        )