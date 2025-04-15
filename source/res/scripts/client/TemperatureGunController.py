# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TemperatureGunController.py
import typing
import BigWorld
from Health import OverheatComponent
import Event
from helpers import dependency
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import getGunSoundObject
from skeletons.gui.battle_session import IBattleSessionProvider
_RTPC_OVERHEAT = 'RTPC_ext_heavy_flamer_overheat'
_COOLING_START_SOUND = 'heavy_flamer_cooling_start'
_COOLING_STOP_SOUND = 'heavy_flamer_cooling_stop'
_OVERHEAT_PERCENT_MULTIPLAYER = 100
_OVERHEAT_MIN_PERCENT = _MIN_TEMPERATURE = _MIN_TIME = 0.0
_OVERHEAT_MAX_PERCENT = 1.0

def getPlayerVehicleTemperatureGunController():
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get('temperatureGunController', None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class TemperatureGunController(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(TemperatureGunController, self).__init__()
        self.__appearanceInited = False
        self.__maxTemperature = _MIN_TEMPERATURE
        self.__overheatPercent = _OVERHEAT_MIN_PERCENT
        self.__statesOverheatCoolingTime = []
        self.__eManager = Event.EventManager()
        self.onTemperatureProgress = Event.Event(self.__eManager)
        self.onSetOverheat = Event.Event(self.__eManager)
        self.onSetState = Event.Event(self.__eManager)
        self.__initTemperatureAppearance()

    @property
    def overheatPercent(self):
        return self.__overheatPercent

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
        self.__maxTemperature = _MIN_TEMPERATURE
        self.__overheatPercent = _OVERHEAT_MIN_PERCENT
        self.__statesOverheatCoolingTime = []
        self.__eManager.clear()

    def onLeaveWorld(self):
        self.onDestroy()

    def getCoolingTime(self):
        if not self.isOverheated:
            return _MIN_TIME
        states = self.entity.typeDescriptor.gun.temperature.states
        stateIndex = self.state
        timeLeft = states[-1].coolingDelay if self.__overheatPercent == _OVERHEAT_MAX_PERCENT else _MIN_TIME
        for index in xrange(stateIndex):
            timeLeft += self.__statesOverheatCoolingTime[index]

        prevMaxTemperature = states[stateIndex - 1].temperature if stateIndex else _MIN_TEMPERATURE
        timeLeft += float(self.temperatureProgress - prevMaxTemperature) / states[stateIndex].coolingOverheatPerSec
        return timeLeft

    def __isAppearanceReady(self):
        player = BigWorld.player()
        if player is None or player.isDisableRespawnMode:
            return False
        elif not self.entity.typeDescriptor.isTemperatureGun:
            return False
        else:
            appearance = self.entity.appearance
            return appearance is not None and appearance.isConstructed

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        temperatureStates = self.entity.typeDescriptor.gun.temperature.states
        self.__maxTemperature = float(temperatureStates[-1].temperature)
        self.__statesOverheatCoolingTime = [_MIN_TIME] * len(temperatureStates)
        if self.__isPlayerVehicle():
            self.__updateTemperatureState()
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
        if self.isOverheated and self.entity.appearance.findComponentByType(OverheatComponent) is None:
            self.entity.appearance.createComponent(OverheatComponent)
        else:
            self.entity.appearance.removeComponentByType(OverheatComponent)
        gunSoundObject = getGunSoundObject(self.entity)
        if self.__isPlayerVehicle() and self.__appearanceInited:
            gunSoundObject.play(_COOLING_START_SOUND if self.isOverheated else _COOLING_STOP_SOUND)
        self.onSetOverheat(self.isOverheated)
        return

    def __cacheOverheatCoolingTime(self):
        temperature = self.entity.typeDescriptor.gun.temperature
        prevMaxTemperature = _MIN_TEMPERATURE
        for index, state in enumerate(temperature.states):
            self.__statesOverheatCoolingTime[index] = float(state.temperature - prevMaxTemperature) / state.coolingOverheatPerSec if state.isOverheated else _MIN_TIME
            prevMaxTemperature = state.temperature

    def __updateTemperatureProgress(self):
        newValue = self.temperatureProgress / self.__maxTemperature if self.__maxTemperature else _OVERHEAT_MIN_PERCENT
        isHeatRemoved = newValue == _MIN_TEMPERATURE
        if isHeatRemoved or self.__overheatPercent == _MIN_TEMPERATURE:
            self.__guiSessionProvider.shared.ammo.setTemperatureGunQuickChangeReady(isHeatRemoved)
        if newValue != self.__overheatPercent:
            self.__overheatPercent = newValue
            getGunSoundObject(self.entity).setRTPC(_RTPC_OVERHEAT, self.__overheatPercent * _OVERHEAT_PERCENT_MULTIPLAYER)
            self.onTemperatureProgress(self.__overheatPercent, self.getCoolingTime())

    def __updateTemperatureState(self):
        self.onSetState(self.state)

    def __isPlayerVehicle(self, player=None):
        player = player or BigWorld.player()
        return player is not None and player.playerVehicleID == self.entity.id
