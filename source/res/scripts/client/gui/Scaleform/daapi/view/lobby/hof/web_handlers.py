# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hof/web_handlers.py
from web_client_api import webApiCollection, w2capi
from web_client_api.ui.browser import CloseBrowserViewWebApiMixin
from web_client_api.vehicles import VehiclesWebApi
from web_client_api.request import RequestWebApi
from web_client_api.sound import SoundWebApi
from web_client_api.ui import OpenWindowWebApi, OpenTabWebApi, ContextMenuWebApi

def createHofWebHandlers():

    @w2capi(name='close_window', key='window_id')
    class _CloseWindowWebApi(CloseBrowserViewWebApiMixin):
        pass

    return webApiCollection(_CloseWindowWebApi, OpenWindowWebApi, OpenTabWebApi, RequestWebApi, SoundWebApi, ContextMenuWebApi, VehiclesWebApi)
