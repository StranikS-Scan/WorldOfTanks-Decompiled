# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_handlers.py
import typing
from web.web_client_api import webApiCollection
from web.web_client_api.battle_pass import BattlePassWebApi
from web.web_client_api.blueprints_convert_sale import BlueprintsConvertSaleWebApi
from web.web_client_api.clans import ClansWebApi
from web.web_client_api.frontline import FrontLineWebApi
from web.web_client_api.mapbox import MapboxWebApi
from web.web_client_api.platform import PlatformWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.ranked_battles import RankedBattlesWebApi
from web.web_client_api.battle_royale import BattleRoyaleWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import HangarSoundWebApi, SoundStateWebApi, SoundWebApi
from web.web_client_api.ui import CloseWindowWebApi, NotificationWebApi, OpenTabWebApi, OpenWindowWebApi, UtilWebApi
from web.web_client_api.vehicles import VehiclesWebApi
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional
_DEFAULT_WEB_API_COLLECTION = (CloseWindowWebApi,
 OpenWindowWebApi,
 NotificationWebApi,
 OpenTabWebApi,
 RequestWebApi,
 ShopWebApi,
 SoundWebApi,
 SoundStateWebApi,
 HangarSoundWebApi,
 UtilWebApi,
 QuestsWebApi,
 VehiclesWebApi,
 RewardsWebApi,
 SocialWebApi,
 BlueprintsConvertSaleWebApi,
 PlatformWebApi,
 MapboxWebApi,
 FrontLineWebApi,
 BattlePassWebApi,
 ClansWebApi,
 RankedBattlesWebApi,
 BattleRoyaleWebApi)

def createWebHandlers(replaces=None):
    handlers = webApiCollection(*_DEFAULT_WEB_API_COLLECTION)
    if replaces:
        replaceHandlers(handlers, replaces)
    return handlers


def replaceHandlers(handlers, nameToApiMap):
    handlersToReplace = [ e for e in handlers if e.name in nameToApiMap.keys() ]
    for element in handlersToReplace:
        handlers.remove(element)

    newHandlers = webApiCollection(*nameToApiMap.values())
    handlers.extend(newHandlers)
