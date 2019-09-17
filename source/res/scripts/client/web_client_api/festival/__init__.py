# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/festival/__init__.py
from web_client_api import w2capi
from web_client_api.festival.advent_calendar import AdventCalendarWebApiMixin
from web_client_api.festival.mini_games import MiniGamesWebApiMixin
from web_client_api.festival.racing import RacingEventWebApiMixin
from web_client_api.festival.shared import HangarTabWebApiMixin

@w2capi(name='fest_19', key='action')
class FestivalWebApi(AdventCalendarWebApiMixin, MiniGamesWebApiMixin, RacingEventWebApiMixin):
    pass


@w2capi(name='open_tab', key='tab_id')
class FestivalOpenTabWebApi(HangarTabWebApiMixin):
    pass
