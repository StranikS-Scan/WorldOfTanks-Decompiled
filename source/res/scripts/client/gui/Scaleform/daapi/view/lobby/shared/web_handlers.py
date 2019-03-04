# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_handlers.py
from web_client_api import webApiCollection
from web_client_api.request import RequestWebApi
from web_client_api.shop import ShopWebApi
from web_client_api.sound import SoundWebApi
from web_client_api.ui import CloseWindowWebApi, UtilWebApi, OpenWindowWebApi, OpenTabWebApi, NotificationWebApi

def createBrowserOverlayWebHandlers():
    return webApiCollection(CloseWindowWebApi, OpenWindowWebApi, NotificationWebApi, OpenTabWebApi, RequestWebApi, ShopWebApi, SoundWebApi, UtilWebApi)
