# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/arena_info_ctrl.py
import BigWorld
import Event
from constants import LOOT_TYPE
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from shared_utils import findFirst
_PROGRESSION_MAXIMUM_DEFAULT = 10
_LOOT_BOX_TIME_DEFAULT = 23

class ArenaInfoController(IArenaLoadController):
    __slots__ = ('__powerPoints', '__maxPowerPoints', '__eventManager', '__bossHealth', '__extraLootBoxTime', 'onBossHealthChanged', 'onPowerPointsChanged', 'onWavesIncoming')

    def __init__(self):
        self.__bossHealth = 0
        self.__powerPoints = 0
        self.__maxPowerPoints = _PROGRESSION_MAXIMUM_DEFAULT
        self.__extraLootBoxTime = _LOOT_BOX_TIME_DEFAULT
        self.__eventManager = Event.EventManager()
        self.onPowerPointsChanged = Event.Event(self.__eventManager)
        self.onWavesIncoming = Event.Event(self.__eventManager)
        self.onBossHealthChanged = Event.Event(self.__eventManager)

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_INFO_CTRL

    def startControl(self, *args):
        arenaInfo = BigWorld.player().arena.arenaInfo
        if arenaInfo is not None:
            self.__bossHealth = arenaInfo.bossHealth
            self.__powerPoints = arenaInfo.powerPoints
            self.__maxPowerPoints = arenaInfo.getWtConfig()['maxPowerPoints']
            self.__extraLootBoxTime = self.__extractTime(arenaInfo.getWtConfig()['loot'])
        return

    def stopControl(self):
        self.__bossHealth = 0
        self.__powerPoints = 0
        self.__eventManager.clear()

    def updateBossHealth(self, value):
        if value != self.__bossHealth:
            self.__bossHealth = value
            self.onBossHealthChanged(self.__bossHealth)

    def updatePowerPoints(self, value):
        if value != self.__powerPoints:
            self.__powerPoints = value
            self.onPowerPointsChanged(self.__powerPoints)

    @property
    def bossHealth(self):
        return self.__bossHealth

    @property
    def powerPoints(self):
        return self.__powerPoints

    @property
    def maxPowerPoints(self):
        return self.__maxPowerPoints

    @property
    def extraLootBoxTime(self):
        return self.__extraLootBoxTime

    @staticmethod
    def __extractTime(loot):
        records = loot.get(LOOT_TYPE.GROUPDROP, [])
        gameTime = findFirst(lambda record: record[0] == 'gameTime', records)
        return gameTime[1][0] if gameTime is not None else _LOOT_BOX_TIME_DEFAULT
