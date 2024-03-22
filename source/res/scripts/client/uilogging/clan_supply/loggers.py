# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/clan_supply/loggers.py
import json
from typing import TYPE_CHECKING
from gui.clans.clan_cache import g_clanCache
from uilogging.base.logger import MetricsLogger
from uilogging.clan_supply.constants import FEATURE, ClanSupplyLogAction
if TYPE_CHECKING:
    from uilogging.types import ItemType, ParentScreenType, InfoType

class ClanSupplyEventLogger(MetricsLogger):
    __slots__ = ('_eventParent',)

    def __init__(self):
        super(ClanSupplyEventLogger, self).__init__(FEATURE)

    def logCloseEvent(self, item, info):
        infoStr = json.dumps({'clan_id': g_clanCache.clanDBID,
         'event_trigger': info.value})
        self.stopAction(action=ClanSupplyLogAction.CLOSE, item=item, info=infoStr)

    def logOpenEvent(self, item, parentScreen):
        self.startAction(ClanSupplyLogAction.CLOSE)
        self.log(action=ClanSupplyLogAction.OPEN, item=item, parentScreen=parentScreen, info=json.dumps({'clan_id': g_clanCache.clanDBID}))
