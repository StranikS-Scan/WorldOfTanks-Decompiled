# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/request/__init__.py
from web_client_api import w2capi
from web_client_api.request.access_token import AccessTokenWebApiMixin
from web_client_api.request.graphics_settings import GraphicsSettingsWebApiMixin
from web_client_api.request.wgni_token import WgniTokenWebApiMixin

@w2capi('request', 'request_id')
class RequestWebApi(AccessTokenWebApiMixin, GraphicsSettingsWebApiMixin, WgniTokenWebApiMixin):
    pass
