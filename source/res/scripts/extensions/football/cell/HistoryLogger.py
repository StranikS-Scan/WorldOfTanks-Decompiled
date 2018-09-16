# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/cell/HistoryLogger.py
import BigWorld
from server_constants import HIST_LOG_CONFIG

class HistoryLogger:

    def __init__(self, logger, historyLength, step, cageBounds):
        self.__historyLength = historyLength
        self.__logger = logger
        self.__clear()
        self.__counter = step
        self.__step = step
        self.__cageBounds = cageBounds

    def append(self, item):
        if not self.isActive():
            return
        self.__items.append(item)
        if len(self.__items) >= self.__historyLength:
            self.commit()

    def commit(self):
        if self.__items:
            self.__logger(self.__items, self.__cageBounds)
            self.__clear()

    def __clear(self):
        self.__items = []

    def isNeedToLog(self):
        if not self.isActive():
            return False
        self.__counter -= 1
        if self.__counter > 0:
            return False
        self.__counter = self.__step
        return True

    def isActive(self):
        return self.__historyLength != 0


def isNeedToLogArena(arenaID):
    if not HIST_LOG_CONFIG.isLogEnabled('football_anticheat_data', BigWorld.globalData):
        return False
    arenaStep = BigWorld.globalData.get('football_arenaLogsStep', HIST_LOG_CONFIG.FOOTBALL_ARENA_STEP)
    return arenaStep != 0 and arenaID % arenaStep == 0
