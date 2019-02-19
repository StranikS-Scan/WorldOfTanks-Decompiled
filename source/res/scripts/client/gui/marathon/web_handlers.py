# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/web_handlers.py
from web_client_api import webApiCollection, w2capi
from web_client_api.marathon import MarathonWebApi
from web_client_api.request.access_token import AccessTokenWebApiMixin
from web_client_api.request.spa_id import SpaIdWebApiMixin
from web_client_api.request.wgni_token import WgniTokenWebApiMixin
from web_client_api.sound import SoundWebApi
from web_client_api.ui import ContextMenuWebApi, OpenWindowWebApi, VehiclePreviewWebApiMixin, UtilWebApi
from web_client_api.ui.hangar import HangarTabWebApiMixin
from web_client_api.ui.profile import ProfileTabWebApiMixin

@w2capi('request', 'request_id')
class _RequestWebApi(AccessTokenWebApiMixin, WgniTokenWebApiMixin, SpaIdWebApiMixin):
    pass


@w2capi(name='open_tab', key='tab_id')
class _OpenTabWebApi(HangarTabWebApiMixin, ProfileTabWebApiMixin, VehiclePreviewWebApiMixin):
    pass


def createMarathonWebHandlers():
    return webApiCollection(SoundWebApi, MarathonWebApi, _OpenTabWebApi, _RequestWebApi, ContextMenuWebApi, OpenWindowWebApi, UtilWebApi)
