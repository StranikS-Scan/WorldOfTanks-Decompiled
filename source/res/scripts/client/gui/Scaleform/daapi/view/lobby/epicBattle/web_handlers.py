# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/web_handlers.py
from web.web_client_api import webApiCollection
from web.web_client_api.frontline import FrontLineWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.sound import SoundWebApi, SoundStateWebApi, HangarSoundWebApi
from web.web_client_api.ui import OpenWindowWebApi, CloseWindowWebApi, OpenTabWebApi, NotificationWebApi, ContextMenuWebApi, UtilWebApi
from web.web_client_api.vehicles import VehiclesWebApi

def createFrontlineWebHandlers():
    return webApiCollection(FrontLineWebApi, VehiclesWebApi, RequestWebApi, ShopWebApi, OpenWindowWebApi, CloseWindowWebApi, OpenTabWebApi, NotificationWebApi, ContextMenuWebApi, UtilWebApi, SoundWebApi, SoundStateWebApi, HangarSoundWebApi, QuestsWebApi)
