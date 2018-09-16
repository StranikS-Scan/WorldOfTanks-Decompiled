# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/web_handlers.py
from web_client_api import webApiCollection
from web_client_api.clans import ClansWebApi
from web_client_api.request import RequestWebApi
from web_client_api.sound import SoundWebApi
from web_client_api.ui import NotificationWebApi, ContextMenuWebApi

def createRankedBattlesWebHandlers():
    return webApiCollection(ClansWebApi, NotificationWebApi, ContextMenuWebApi, RequestWebApi, SoundWebApi)
