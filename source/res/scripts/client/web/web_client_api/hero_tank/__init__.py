# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/hero_tank/__init__.py
from web.web_client_api import w2capi
from web.web_client_api.hero_tank.vehicle import HeroTankWebApiMixin

@w2capi(name='hero_tank', key='action')
class HeroTankWebApi(HeroTankWebApiMixin):
    pass
