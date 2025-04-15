# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBAvatarComponent.py
import typing
import BigWorld
import Event
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from script_component.ScriptComponent import ScriptComponent
if typing.TYPE_CHECKING:
    from Avatar import Avatar

class HBAvatarComponent(ScriptComponent):
    onSpawn = Event.Event()
    onRespawn = Event.Event()
    onDeath = Event.Event()
    onRespawnExhaused = Event.Event()

    def __init__(self):
        super(HBAvatarComponent, self).__init__()
        g_playerEvents.onArenaPeriodChange += self.__onPeriodChanged
        self.__isSpawn = False

    @property
    def avatar(self):
        return self.entity

    def onLeaveWorld(self):
        g_playerEvents.onArenaPeriodChange -= self.__onPeriodChanged
        super(HBAvatarComponent, self).onLeaveWorld()

    def selectVehicle(self, vehTypeCD):
        self.cell.selectVehicle(vehTypeCD)

    def confirmVehicleSelection(self):
        self.cell.confirmVehicleSelection()

    def getAliveVehicleCount(self):
        return sum(self.tankSetMask)

    def set_respawnPrepared(self, _):
        if self.__isSpawn:
            self.onSpawn(self.avatar.id)
            self.__isSpawn = False
        elif self.respawnPrepared:
            self.onDeath(self.avatar.id, self.respawnTime)
        else:
            self.onRespawn(self.avatar.id)

    def set_respawnsExhausted(self, _):
        if self.respawnsExhausted:
            self.onDeath(self.avatar.id, 0)
            self.onRespawnExhaused()

    def __onPeriodChanged(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.PREBATTLE:
            timeLeft = periodEndTime - BigWorld.serverTime()
            self.cell.prepareSpawn(timeLeft)
            self.__isSpawn = True
