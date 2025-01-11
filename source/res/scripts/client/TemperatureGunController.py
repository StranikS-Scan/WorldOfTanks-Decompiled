# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TemperatureGunController.py
import typing
import BigWorld
import Health
import Event
from auto_shoot_guns.auto_shoot_guns_common import autoShootDynamicAttrFactors
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import getGunSoundObject
from helpers import dependency
from items.attributes_helpers import onCollectAttributes, AUTOSHOOT_ATTR_PREFIX
from shared_utils import findFirst
from skeletons.gui.battle_session import IBattleSessionProvider
_RTPC_OVERHEAT = 'RTPC_ext_heavy_flamer_overheat'
_COOLING_START_SOUND = 'heavy_flamer_cooling_start'
_COOLING_STOP_SOUND = 'heavy_flamer_cooling_stop'
_OVERHEAT_PERCENT_MULTIPLAYER = 100
_OVERHEAT_MIN_PERCENT = 0.0
_MIN_TEMPERATURE = 0.0
_MIN_TIME = 0.0
_MAX_TEMPERATURE_PROGRESS = 1.0

def getPlayerVehicleTemperatureGunController():
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get('temperatureGunController', None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class TemperatureGunController(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TemperatureGunController, self).__init__()
        self.__appearanceInited = False
        self.__maxTemperature = self.__overheatMark = _MIN_TEMPERATURE
        self.__overheatPercent = _OVERHEAT_MIN_PERCENT
        self.__overheatStartTime = None
        self.__currAutoShootFactors = autoShootDynamicAttrFactors()
        self.__statesAutoShootFactors = []
        self.__statesOverheatCoolingTime = []
        self.__eManager = Event.EventManager()
        self.onTemperatureProgress = Event.Event(self.__eManager)
        self.onSetOverheat = Event.Event(self.__eManager)
        self.__initTemperatureAppearance()
        return

    @property
    def overheatPercent(self):
        return self.__overheatPercent

    @property
    def overheatMarkPercent(self):
        return self.__overheatMark / self.__maxTemperature if self.__maxTemperature else _OVERHEAT_MIN_PERCENT

    def getAutoShootRateFactor(self):
        return self.__currAutoShootFactors['rate/multiplier']

    def set_state(self, _=None):
        if self.__appearanceInited and self.__isAppearanceReady():
            self.__updateTemperatureState()

    def set_temperatureProgress(self, _=None):
        if self.__appearanceInited and self.__isAppearanceReady():
            self.__updateTemperatureProgress()

    def set_isOverheated(self, _=None):
        if self.__appearanceInited and self.__isAppearanceReady():
            self.__updateTemperatureOverheat()

    def onDestroy(self):
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        self.__appearanceInited = False
        self.__maxTemperature = self.__overheatMark = _MIN_TEMPERATURE
        self.__overheatPercent = _OVERHEAT_MIN_PERCENT
        self.__overheatStartTime = None
        self.__currAutoShootFactors = autoShootDynamicAttrFactors()
        self.__statesAutoShootFactors = []
        self.__statesOverheatCoolingTime = []
        self.__eManager.clear()
        return

    def onLeaveWorld(self):
        self.onDestroy()

    def calculateCoolingTime(self):
        if not self.isOverheated:
            return _MIN_TIME
        else:
            temperature = self.entity.typeDescriptor.gun.temperature
            coolingDelay = _MIN_TIME
            if self.__overheatStartTime is not None:
                overheatTimeDiff = BigWorld.time() - self.__overheatStartTime
                coolingDelay = temperature.states[-1].coolingDelay - overheatTimeDiff
            timeLeft = max(coolingDelay, 0.0)
            stateIndex = self.state
            prevMaxTemperature = temperature.states[stateIndex - 1].temperature if stateIndex else _MIN_TEMPERATURE
            for index, state in enumerate(temperature.states):
                if state.isOverheated and index < stateIndex:
                    timeLeft += self.__statesOverheatCoolingTime[index]

            timeLeft += float(self.temperatureProgress - prevMaxTemperature) / temperature.states[stateIndex].coolingOverheatPerSec
            return timeLeft

    def __isAppearanceReady(self):
        player = BigWorld.player()
        if player is None or player.isDisableRespawnMode:
            return False
        else:
            temperature = self.entity.typeDescriptor.gun.temperature
            if temperature is None:
                return False
            appearance = self.entity.appearance
            return appearance is not None and appearance.isConstructed

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        temperatureStates = self.entity.typeDescriptor.gun.temperature.states
        self.__maxTemperature = float(temperatureStates[-1].temperature)
        overheatMarkState = findFirst(lambda s: not s.isOverheated, reversed(temperatureStates))
        self.__overheatMark = overheatMarkState.temperature if overheatMarkState else _MIN_TEMPERATURE
        self.__statesAutoShootFactors = [ autoShootDynamicAttrFactors() for _ in temperatureStates ]
        for factors, state in zip(self.__statesAutoShootFactors, temperatureStates):
            onCollectAttributes(factors, [state.modifiers], AUTOSHOOT_ATTR_PREFIX, False)

        self.__statesOverheatCoolingTime = [_MIN_TIME] * len(temperatureStates)
        self.__updateTemperatureState()
        if self.__isPlayerVehicle():
            self.__updateTemperatureProgress()
            self.__cacheOverheatCoolingTime()
        self.__updateTemperatureOverheat()
        self.__appearanceInited = True

    def __initTemperatureAppearance(self):
        if self.__isAppearanceReady():
            self.__onAppearanceReady()
        else:
            self.entity.onAppearanceReady += self.__onAppearanceReady

    def __updateTemperatureOverheat(self):
        if self.isOverheated:
            if self.entity.appearance.findComponentByType(Health.OverheatComponent) is None:
                self.entity.appearance.createComponent(Health.OverheatComponent)
            self.__overheatStartTime = BigWorld.time()
        else:
            self.entity.appearance.removeComponentByType(Health.OverheatComponent)
            self.__overheatStartTime = None
        self.__playOverheatSound()
        self.onSetOverheat(self.isOverheated)
        return

    def __cacheOverheatCoolingTime(self):
        temperature = self.entity.typeDescriptor.gun.temperature
        prevMaxTemperature = _MIN_TEMPERATURE
        for index, state in enumerate(temperature.states):
            if state.isOverheated:
                self.__statesOverheatCoolingTime[index] = float(state.temperature - prevMaxTemperature) / state.coolingOverheatPerSec
            prevMaxTemperature = state.temperature

    def __playOverheatSound(self):
        gunSoundObject = getGunSoundObject(self.entity)
        if self.__isPlayerVehicle() and self.__appearanceInited:
            gunSoundObject.play(_COOLING_START_SOUND if self.isOverheated else _COOLING_STOP_SOUND)

    def __updateTemperatureProgress(self):
        newValue = self.temperatureProgress / self.__maxTemperature if self.__maxTemperature else _OVERHEAT_MIN_PERCENT
        isHeatRemoved = newValue == _MIN_TEMPERATURE
        if isHeatRemoved or self.__overheatPercent == _MIN_TEMPERATURE:
            self.__guiSessionProvider.shared.ammo.setTemperatureGunQuickChangeReady(isHeatRemoved)
        if newValue != self.__overheatPercent:
            self.__overheatPercent = newValue
            getGunSoundObject(self.entity).setRTPC(_RTPC_OVERHEAT, self.__overheatPercent * _OVERHEAT_PERCENT_MULTIPLAYER)
            self.onTemperatureProgress(self.__overheatPercent)

    def __updateTemperatureState(self):
        self.__currAutoShootFactors = self.__statesAutoShootFactors[self.state]

    def __isPlayerVehicle(self, player=None):
        player = player or BigWorld.player()
        return player is not None and player.playerVehicleID == self.entity.id
