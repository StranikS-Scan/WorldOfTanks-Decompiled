# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_handlers.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.marathon.bob_event import BobEvent
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController, IBobController
from web.web_client_api import webApiCollection
from web.web_client_api.frontline import FrontLineWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import SoundWebApi, HangarSoundWebApi, SoundStateWebApi
from web.web_client_api.ui import CloseWindowWebApi, UtilWebApi, OpenWindowWebApi, OpenTabWebApi, NotificationWebApi
from web.web_client_api.vehicles import VehiclesWebApi
_DEFAULT_WEB_API_COLLECTION = (CloseWindowWebApi,
 OpenWindowWebApi,
 NotificationWebApi,
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
 FrontLineWebApi)

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


def createBrowserOverlayWebHandlers():
    return webApiCollection(OpenTabWebApi, *_DEFAULT_WEB_API_COLLECTION)


def createPremAccWebHandlers():
    return webApiCollection(OpenTabWebApi, *_DEFAULT_WEB_API_COLLECTION)


def createBobOverlayWebHandlers():
    return webApiCollection(_OpenBobTabWebApi, *_DEFAULT_WEB_API_COLLECTION)
