# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/web_handlers.py
from functools import partial
from gui.marathon.racing_event import RacingEvent
from gui.server_events.events_dispatcher import showMissionsMarathon
from web_client_api import webApiCollection, w2capi
from web_client_api.festival import FestivalWebApi
from web_client_api.quests import QuestsWebApi
from web_client_api.request.access_token import AccessTokenWebApiMixin
from web_client_api.request.spa_id import SpaIdWebApiMixin
from web_client_api.request.wgni_token import WgniTokenWebApiMixin
from web_client_api.rewards import RewardsWebApi
from web_client_api.shop import ShopWebApi
from web_client_api.social import SocialWebApi
from web_client_api.sound import SoundWebApi, SoundStateWebApi, HangarSoundWebApi, SoundPlay2DWebApi, SoundStop2DWebApi, GlobalSoundStateWebApi
from web_client_api.ui import ContextMenuWebApi, OpenWindowWebApi, VehiclePreviewWebApiMixin, UtilWebApi, CloseWindowWebApi, NotificationWebApi
from web_client_api.ui.hangar import HangarTabWebApiMixin
from web_client_api.ui.profile import ProfileTabWebApiMixin
from web_client_api.vehicles import VehiclesWebApi
_DEFAULT_MARATHON_WEB_API_COLLECTION = (SoundWebApi,
 SoundStateWebApi,
 SoundPlay2DWebApi,
 SoundStop2DWebApi,
 GlobalSoundStateWebApi,
 HangarSoundWebApi,
 QuestsWebApi,
 VehiclesWebApi,
 ContextMenuWebApi,
 OpenWindowWebApi,
 CloseWindowWebApi,
 NotificationWebApi,
 UtilWebApi,
 ShopWebApi,
 FestivalWebApi,
 RewardsWebApi,
 SocialWebApi)

@w2capi('request', 'request_id')
class _RequestWebApi(AccessTokenWebApiMixin, WgniTokenWebApiMixin, SpaIdWebApiMixin):
    pass


@w2capi(name='open_tab', key='tab_id')
class _OpenTabWebApi(HangarTabWebApiMixin, ProfileTabWebApiMixin, VehiclePreviewWebApiMixin):

    def _getVehicleStylePreviewCallback(self):
        return showMissionsMarathon


@w2capi(name='open_tab', key='tab_id')
class _RacingEventOpenTabWebApi(HangarTabWebApiMixin, ProfileTabWebApiMixin, VehiclePreviewWebApiMixin):

    def _getVehicleStylePreviewCallback(self):
        return partial(showMissionsMarathon, RacingEvent.RACING_MARATHON_PREFIX)


def createDefaultMarathonWebHandlers():
    return webApiCollection(_OpenTabWebApi, _RequestWebApi, *_DEFAULT_MARATHON_WEB_API_COLLECTION)


def createRacingEventWebHandlers():
    return webApiCollection(_RacingEventOpenTabWebApi, _RequestWebApi, *_DEFAULT_MARATHON_WEB_API_COLLECTION)
