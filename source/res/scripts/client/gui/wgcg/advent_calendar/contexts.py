# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/advent_calendar/contexts.py
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType

class AdventCalendarFetchHeroTankInfoCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.ADVENT_CALENDAR_FETCH_HERO_TANK_INFO

    def isAuthorizationRequired(self):
        return False

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False
