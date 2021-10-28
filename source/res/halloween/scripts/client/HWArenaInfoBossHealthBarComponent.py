# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWArenaInfoBossHealthBarComponent.py
import logging
import BigWorld
import Event
_logger = logging.getLogger(__name__)

class HWArenaInfoBossHealthBarComponent(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(HWArenaInfoBossHealthBarComponent, self).__init__()
        self.__isActive = False
        self.__bossHealth = 0
        self.__phase = -1
        self.__phaseHealth = None
        self._eventManager = Event.EventManager()
        self.onBossHealthPrepared = Event.Event(self._eventManager)
        self.onBossHealthChanged = Event.Event(self._eventManager)
        self.__activate()
        return

    def set_lastBossHealth(self, _):
        self.__bossHealth = self.lastBossHealth
        if not self.__isActive:
            return
        if self.__updatePhase(self.__bossHealth):
            self.__updateMarkerMaxHealth(self.__bossHealth)
        self.onBossHealthChanged()

    def set_healthPhases(self, _):
        if self.__activate():
            self.onBossHealthPrepared()
        else:
            _logger.error('Connot activate the component with data: %d, %d and %s', self.bossVehicleId, self.__bossHealth, self.healthPhases)

    @property
    def isActive(self):
        return self.__isActive

    @property
    def bossId(self):
        return self.bossVehicleId

    def getBossMarkerCurrentHealthValues(self):
        return self.getVehicleMarkerHealthValues(self.__bossHealth)

    def getCurrentUIPhase(self):
        return self.__phaseCount - self.__phase + 1

    def getVehicleMarkerHealthValues(self, health):
        if not self.isActive:
            return (health, health)
        phase = self.__getFightPhase(health)
        phaseMinHealth, phaseMaxHealth = self.__getPhaseMinMaxHealth(phase)
        currentHealth = health - phaseMinHealth
        maxHealth = phaseMaxHealth - phaseMinHealth
        _logger.info('Retrieve the marker current health %d and max %d health from the vehicle health %d', currentHealth, maxHealth, health)
        return (currentHealth, maxHealth)

    def __getPhaseMinMaxHealth(self, phase):
        phaseMaxHealth = self.__phaseHealth[phase - 1]
        phaseMinHealth = self.__phaseHealth[phase + 0]
        return (phaseMinHealth, phaseMaxHealth)

    def __checkIfValid(self):
        return self.bossVehicleId and self.bossVehicleId > 0 and self.healthPhases and len(self.healthPhases)

    def __activate(self):
        if not self.__checkIfValid():
            return False
        self.__isActive = True
        if self.lastBossHealth and self.lastBossHealth > 0:
            health = self.lastBossHealth
        elif self.bossId in BigWorld.entities.get(self.bossId):
            vehicle = BigWorld.entities[self.bossId]
            health = vehicle.health
        else:
            _logger.error('The boss lastBossHealth is not set. Use the default value.')
            health = self.__phaseHealth[0]
        self.__bossHealth = health
        self.__phaseHealth = self.healthPhases + (0,)
        self.__updatePhase(health)
        self.__updateMarkerMaxHealth(health)
        return True

    def __updatePhase(self, health):
        phase = self.__getFightPhase(health)
        isChanged = phase != self.__phase
        if isChanged:
            self.__phase = phase
        return isChanged

    @property
    def __phaseCount(self):
        return len(self.__phaseHealth) - 1

    def __getFightPhase(self, health):
        for phase in range(1, self.__phaseCount):
            if health > self.__phaseHealth[phase]:
                return phase

        return self.__phaseCount

    def __updateMarkerMaxHealth(self, health):
        guiSessionProvider = BigWorld.player().guiSessionProvider
        guiSessionProvider.setVehicleMaxHealth(False, self.bossVehicleId, health)
