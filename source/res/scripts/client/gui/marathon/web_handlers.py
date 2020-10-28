# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/web_handlers.py
from gui.server_events.events_dispatcher import showMissionsMarathon
from web.web_client_api import webApiCollection, w2capi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.request.access_token import AccessTokenWebApiMixin
from web.web_client_api.request.spa_id import SpaIdWebApiMixin
from web.web_client_api.request.wgni_token import WgniTokenWebApiMixin
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import HangarSoundWebApi, SoundStateWebApi
from web.web_client_api.ui import CloseWindowWebApi, NotificationWebApi
from web.web_client_api.sound import SoundWebApi
from web.web_client_api.ui import ContextMenuWebApi, OpenWindowWebApi, VehiclePreviewWebApiMixin, UtilWebApi
from web.web_client_api.ui.hangar import HangarTabWebApiMixin
from web.web_client_api.ui.profile import ProfileTabWebApiMixin
from web.web_client_api.vehicles import VehiclesWebApi
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
class _OpenTabWebApi(HangarTabWebApiMixin, ProfileTabWebApiMixin, VehiclePreviewWebApiMixin):

    def _getVehicleStylePreviewCallback(self, cmd):
        return showMissionsMarathon


def createDefaultMarathonWebHandlers():
    return webApiCollection(_OpenTabWebApi, _RequestWebApi, *_DEFAULT_MARATHON_WEB_API_COLLECTION)
