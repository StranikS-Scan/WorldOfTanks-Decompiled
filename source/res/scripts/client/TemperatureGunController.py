# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TemperatureGunController.py
import typing
import Event
import Statuses
from auto_shoot_guns.auto_shoot_guns_common import autoShootDynamicAttrFactors
from items.attributes_helpers import onCollectAttributes, AUTOSHOOT_ATTR_PREFIX
from shared_utils import findFirst
from vehicle_systems.entity_components.vehicle_mechanic_component import ifAppearanceReady, getPlayerVehicleMechanic, VehicleMechanicComponent

def getPlayerVehicleTemperatureGunController():
    return getPlayerVehicleMechanic('temperatureGunController')


class TemperatureGunController(VehicleMechanicComponent):

    def __init__(self):
        super(TemperatureGunController, self).__init__()
        self.__maxTemperature = 0.0
        self.__overheatMark = 0.0
        self.__statesAutoShootFactors = []
        self.__overheatProgress = 0.0
        self.__currAutoShootFactors = autoShootDynamicAttrFactors()
        self.__eManager = Event.EventManager()
        self.onTemperatureProgress = Event.Event(self.__eManager)
        self.onSetOverheat = Event.Event(self.__eManager)
        self._initMechanic()

    @property
    def overheatProgress(self):
        return self.__overheatProgress

    @property
    def overheatMarkPercent(self):
        return self.__overheatMark / self.__maxTemperature if self.__maxTemperature else 0.0

    def getAutoShootRateFactor(self):
        return self.__currAutoShootFactors['rate/multiplier']

    @ifAppearanceReady
    def set_state(self, _=None):
        self.__updateTemperatureState()

    @ifAppearanceReady
    def set_temperatureProgress(self, _=None):
        self.__updateTemperatureProgress()

    @ifAppearanceReady
    def set_isOverheated(self, _=None):
        self.__updateTemperatureOverheat()

    def onDestroy(self):
        self.__eManager.clear()
        super(TemperatureGunController, self).onDestroy()

    def _onAppearanceReady(self):
        temperatureSates = self.entity.typeDescriptor.gun.temperature.states
        self.__maxTemperature = float(temperatureSates[-1].temperature)
        overheatMarkState = findFirst(lambda s: not s.isOverheated, reversed(temperatureSates))
        self.__overheatMark = overheatMarkState.temperature if overheatMarkState else 0.0
        self.__statesAutoShootFactors = [ autoShootDynamicAttrFactors() for _ in temperatureSates ]
        for factors, state in zip(self.__statesAutoShootFactors, temperatureSates):
            onCollectAttributes(factors, [state.modifiers], AUTOSHOOT_ATTR_PREFIX, False)

    def _onMechanicAppearanceUpdate(self):
        self.__updateTemperatureState()
        self.__updateTemperatureProgress()
        self.__updateTemperatureOverheat()

    def __updateTemperatureState(self):
        self.__currAutoShootFactors = self.__statesAutoShootFactors[self.state]

    def __updateTemperatureProgress(self):
        self.__overheatProgress = self.temperatureProgress / self.__maxTemperature
        self.onTemperatureProgress(self.__overheatProgress)

    def __updateTemperatureOverheat(self):
        appearance = self.entity.appearance
        if not self.isOverheated:
            appearance.removeComponentByType(Statuses.OverheatComponent)
        elif appearance.findComponentByType(Statuses.OverheatComponent) is None:
            appearance.createComponent(Statuses.OverheatComponent)
        self.onSetOverheat(self.isOverheated)
        return
