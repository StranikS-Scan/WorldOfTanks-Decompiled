# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_handlers.py
from web_client_api import webApiCollection
from web_client_api.request import RequestWebApi
from web_client_api.sound import SoundWebApi, HangarSoundWebApi
from web_client_api.ui import CloseWindowWebApi, UtilWebApi, ContextMenuWebApi, OpenWindowWebApi, OpenTabWebApi, NotificationWebApi
from web_client_api.vehicles import VehiclesWebApi

def createBrowserOverlayWebHandlers():
    return webApiCollection(SoundWebApi, HangarSoundWebApi, VehiclesWebApi, RequestWebApi, OpenWindowWebApi, CloseWindowWebApi, OpenTabWebApi, NotificationWebApi, ContextMenuWebApi, UtilWebApi)
