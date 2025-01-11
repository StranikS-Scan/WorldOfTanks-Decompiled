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
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.marathon.bob_event import BobEvent
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController, IBobController
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import HangarSoundWebApi, SoundStateWebApi, SoundWebApi
from web.web_client_api.ui import CloseWindowWebApi, NotificationWebApi, OpenTabWebApi, OpenWindowWebApi, UtilWebApi
from web.web_client_api.uilogging import UILoggingWebApi
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
 BattleRoyaleWebApi,
 UILoggingWebApi)

def createWebHandlers(replaces=None):
    handlers = webApiCollection(*_DEFAULT_WEB_API_COLLECTION)
    if replaces:
        replaceHandlers(handlers, replaces)
    return handlers


class _OpenBobTabWebApi(OpenTabWebApi):

    def _getVehicleStylePreviewCallback(self, cmd):

        def callback():
            marathonsCtrl = dependency.instance(IMarathonEventsController)
            bobController = dependency.instance(IBobController)
            if bobController.lactOpenedBobUrl:
                bobEvent = marathonsCtrl.getMarathon(BobEvent.BOB_EVENT_PREFIX)
                bobEvent.setAdditionalUrl(bobController.lactOpenedBobUrl)
                showMissionsMarathon(BobEvent.BOB_EVENT_PREFIX)
            showBrowserOverlayView(cmd.back_url, alias=VIEW_ALIAS.BOB_OVERLAY_CONTENT_VIEW)

        return callback


def replaceHandlers(handlers, nameToApiMap):
    handlersToReplace = [ e for e in handlers if e.name in nameToApiMap.keys() ]
    for element in handlersToReplace:
        handlers.remove(element)

    newHandlers = webApiCollection(*nameToApiMap.values())
    handlers.extend(newHandlers)


def createBobOverlayWebHandlers():
    return webApiCollection(_OpenBobTabWebApi, *_DEFAULT_WEB_API_COLLECTION)
