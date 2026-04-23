# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBAvatarRespawnComponent.py
import typing
import Event
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from helpers import dependency
from script_component.ScriptComponent import ScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from Avatar import Avatar

class HBAvatarRespawnComponent(ScriptComponent):
    onDivisionDataInited = Event.SafeEvent()
    onSpawn = Event.SafeEvent()
    onRespawn = Event.SafeEvent()
    onDeath = Event.SafeEvent()
    onRespawnExhausted = Event.SafeEvent()
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(HBAvatarRespawnComponent, self).__init__()
        g_playerEvents.onArenaPeriodChange += self.__onPeriodChanged
        self.__isSpawn = False

    @property
    def avatar(self):
        return self.entity

    def onLeaveWorld(self):
        g_playerEvents.onArenaPeriodChange -= self.__onPeriodChanged
        super(HBAvatarRespawnComponent, self).onLeaveWorld()

    def hasDivisionData(self):
        return len(self.tankSet) > 0

    def selectVehicle(self, vehTypeCD):
        self.cell.selectVehicle(vehTypeCD)

    def confirmVehicleSelection(self):
        self.cell.confirmVehicleSelection()

    def getAliveVehicleCount(self):
        return sum(self.tankSetMask)

    def set_tankSet(self, _):
        if self.hasDivisionData():
            self.onDivisionDataInited(self.tankSet)

    def set_respawnPrepared(self, _):
        if self.__isSpawn:
            self.__spawnPrepared()
            return
        if self.respawnPrepared:
            self.onDeath(self.respawnTime)
        else:
            self.onRespawn()

    def set_respawnsExhausted(self, _):
        if self.respawnsExhausted:
            self.onDeath(0)
            self.onRespawnExhausted()

    def _onAvatarReady(self):
        arenaPeriod = self.__sessionProvider.shared.arenaPeriod
        self.__isSpawn = arenaPeriod.getPeriod() == ARENA_PERIOD.PREBATTLE
        if self.__isSpawn:
            self.__spawnPrepared()

    def __onPeriodChanged(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        self.__isSpawn = period == ARENA_PERIOD.PREBATTLE
        if self.__isSpawn:
            self.__spawnPrepared()

    def __spawnPrepared(self):
        if self.respawnPrepared and not self.__hadRespawn():
            self.onSpawn()
            self.__isSpawn = False

    def __hadRespawn(self):
        return self.getAliveVehicleCount() < len(self.tankSet)
