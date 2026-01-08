# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ExtraShotClipComponent.py
from constants import ExtraShotClipStates
from events_handler import eventHandler
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState, AmmoShootPossibility
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class ExtraShotAmmoState(DefaultComponentAmmoState):

    def __init__(self, reloadState):
        super(ExtraShotAmmoState, self).__init__()
        self.__reloadState = reloadState

    @property
    def extraReloadState(self):
        return self.__reloadState

    def isReloadAfterShot(self, timeLeft, baseTime):
        return self.__reloadState & ExtraShotClipStates.FULL_RELOAD_WITH_EXTRA_TIME if self.__reloadState & ExtraShotClipStates.EXTRA_FULL_RELOAD else timeLeft == baseTime

    def getShootPossibility(self, currentShells):
        isShootPossible = currentShells[1] == 1 and self.__reloadState == ExtraShotClipStates.EXTRA_FULL_RELOAD
        return AmmoShootPossibility.ALLOWED if isShootPossible else AmmoShootPossibility.NOT_DEFINED


@ReprInjector.withParent()
class ExtraShotClipComponent(VehicleDynamicComponent, IGunMechanicComponent):

    def __init__(self):
        super(ExtraShotClipComponent, self).__init__()
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.EXTRA_SHOT_CLIP

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = ExtraShotAmmoState(self.reloadState)
