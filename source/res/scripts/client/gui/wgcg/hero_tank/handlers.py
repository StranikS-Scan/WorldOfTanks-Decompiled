# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/hero_tank/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class AdventCalendarRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.HERO_TANK_GET_LIST: self.__getHeroTanksList}
        return handlers

    def __getHeroTanksList(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, ('advent_calendar', 'get_hero_tanks_list'))
