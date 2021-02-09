# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/web_handlers.py
from functools import partial
from gui.marathon.bob_event import BobEvent
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared.event_dispatcher import showStorage
from helpers import dependency
from skeletons.gui.game_control import IMarathonEventsController, IBobSoundController
from web.web_client_api import webApiCollection, w2capi
from web.web_client_api.bob import BobWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.request.access_token import AccessTokenWebApiMixin
from web.web_client_api.request.spa_id import SpaIdWebApiMixin
from web.web_client_api.request.wgni_token import WgniTokenWebApiMixin
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import HangarSoundWebApi, SoundStateWebApi
from web.web_client_api.ui import CloseWindowWebApi, NotificationWebApi, OpenTabWebApi
from web.web_client_api.sound import SoundWebApi
from web.web_client_api.ui import ContextMenuWebApi, OpenWindowWebApi, VehiclePreviewWebApiMixin, UtilWebApi
from web.web_client_api.ui.hangar import HangarTabWebApiMixin
from web.web_client_api.ui.missions import MissionsWebApiMixin
from web.web_client_api.ui.profile import ProfileTabWebApiMixin
from web.web_client_api.vehicles import VehiclesWebApi
from web.web_client_api.ui.shop import ShopWebApiMixin
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
_DEFAULT_MARATHON_WEB_API_COLLECTION = (SoundWebApi,
 SoundStateWebApi,
 HangarSoundWebApi,
 QuestsWebApi,
 VehiclesWebApi,
 ContextMenuWebApi,
 OpenWindowWebApi,
 CloseWindowWebApi,
 NotificationWebApi,
 UtilWebApi,
 ShopWebApi,
 RewardsWebApi,
 SocialWebApi)

@w2capi('request', 'request_id')
class _RequestWebApi(AccessTokenWebApiMixin, WgniTokenWebApiMixin, SpaIdWebApiMixin):
    pass


@w2capi(name='open_tab', key='tab_id')
class _OpenTabWebApi(HangarTabWebApiMixin, ProfileTabWebApiMixin, ShopWebApiMixin, VehiclePreviewWebApiMixin, MissionsWebApiMixin):

    def _getVehicleStylePreviewCallback(self, cmd):
        return partial(showStorage, defaultSection=STORAGE_CONSTANTS.CUSTOMIZATION) if cmd.back_btn_descr == 'storage' else showMissionsMarathon


@w2capi(name='open_tab', key='tab_id')
class _OpenTabBobWebApi(OpenTabWebApi):
    __bobSounds = dependency.descriptor(IBobSoundController)

    def _showStylePreview(self, vehicleCD, cmd):
        self.__bobSounds.onStylePreviewOpen()
        super(_OpenTabBobWebApi, self)._showStylePreview(vehicleCD, cmd)

    def _getVehicleStylePreviewCallback(self, cmd):
        if cmd.back_url:
            marathonsCtrl = dependency.instance(IMarathonEventsController)
            bobEvent = marathonsCtrl.getMarathon(BobEvent.BOB_EVENT_PREFIX)
            bobEvent.setAdditionalUrl(cmd.back_url)
        return partial(showMissionsMarathon, BobEvent.BOB_EVENT_PREFIX)


def createDefaultMarathonWebHandlers():
    return webApiCollection(_OpenTabWebApi, _RequestWebApi, *_DEFAULT_MARATHON_WEB_API_COLLECTION)


def createBobWebHandlers():
    return webApiCollection(BobWebApi, _OpenTabBobWebApi, _RequestWebApi, *_DEFAULT_MARATHON_WEB_API_COLLECTION)
