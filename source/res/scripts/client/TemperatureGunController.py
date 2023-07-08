# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TemperatureGunController.py
import typing
import BigWorld
import Health
import Event
from auto_shoot_guns.auto_shoot_guns_common import autoShootDynamicAttrFactors
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import getGunSoundObject
from items.attributes_helpers import onCollectAttributes, AUTOSHOOT_ATTR_PREFIX
from shared_utils import findFirst

def getPlayerVehicleTemperatureGunController():
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get('temperatureGunController', None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class TemperatureGunController(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(TemperatureGunController, self).__init__()
        self.__appearanceInited = False
        self.__maxTemperature = 0.0
        self.__overheatPercent = self.__overheatMark = 0.0
        self.__currAutoShootFactors = autoShootDynamicAttrFactors()
        self.__statesAutoShootFactors = []
        self.__eManager = Event.EventManager()
        self.onTemperatureProgress = Event.Event(self.__eManager)
        self.onSetOverheat = Event.Event(self.__eManager)
        self.__initTemperatureAppearance()

    @property
    def overheatPercent(self):
        return self.__overheatPercent

    @property
    def overheatMarkPercent(self):
        return self.__overheatMark / self.__maxTemperature if self.__maxTemperature else 0.0

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
        self.__eManager.clear()

    def onLeaveWorld(self):
        self.onDestroy()

    def __isAppearanceReady(self):
        appearance = self.entity.appearance
        return appearance is not None and appearance.isConstructed

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        temperature = self.entity.typeDescriptor.gun.temperature
        self.__maxTemperature = float(temperature.states[-1].temperature)
        overheatMarkState = findFirst(lambda s: not s.isOverheated, reversed(temperature.states))
        self.__overheatMark = overheatMarkState.temperature if overheatMarkState else 0.0
        self.__statesAutoShootFactors = [ autoShootDynamicAttrFactors() for _ in temperature.states ]
        for factors, state in zip(self.__statesAutoShootFactors, temperature.states):
            onCollectAttributes(factors, [state.modifiers], AUTOSHOOT_ATTR_PREFIX, False)

        self.__updateTemperatureState()
        self.__updateTemperatureProgress()
        self.__updateTemperatureOverheat()
        self.__appearanceInited = True

    def __initTemperatureAppearance(self):
        if self.__isAppearanceReady():
            self.__onAppearanceReady()
        else:
            self.entity.onAppearanceReady += self.__onAppearanceReady

    def __updateTemperatureOverheat(self):
        if not self.isOverheated:
            self.entity.appearance.removeComponentByType(Health.OverheatComponent)
        elif self.entity.appearance.findComponentByType(Health.OverheatComponent) is None:
            self.entity.appearance.createComponent(Health.OverheatComponent)
        self.onSetOverheat(self.isOverheated)
        return

    def __updateTemperatureProgress(self):
        self.__overheatPercent = self.temperatureProgress / self.__maxTemperature if self.__maxTemperature else 0.0
        getGunSoundObject(self.entity).setRTPC('RTPC_ext_acann_overheat', self.__overheatPercent * 100)
        self.onTemperatureProgress(self.__overheatPercent)

    def __updateTemperatureState(self):
        self.__currAutoShootFactors = self.__statesAutoShootFactors[self.state]
