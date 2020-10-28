# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/events/__init__.py
from web.web_client_api import w2capi
from web.web_client_api.events.halloween import Halloween19WebApiMixin

@w2capi(name='halloween_data', key='action')
class EventsWebApi(Halloween19WebApiMixin):
    pass
