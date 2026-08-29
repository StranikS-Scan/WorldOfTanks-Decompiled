# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ShellCalibrationController.py
from __future__ import absolute_import
from constants import SHELL_CALIBRATION_STATE
from collections import namedtuple
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.components.vehicle_prefabs import createMechanicPrefabSpawner
from vehicles.mechanics.generic_mechanics.shell_calibration.mechanic_models import ShellCalibrationAmmoState
from vehicles.mechanics.gun_mechanics.common import IGunMechanicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleDescrMechanicParams
from vehicles.mechanics.mechanic_states import IMechanicStatesComponent, createMechanicStatesEvents, IMechanicStatesEvents, IMechanicState

@ReprInjector.simple('isPenBonusActive', 'isNonPenBonusActive')
class ShellCalibrationModeState(namedtuple('ShellCalibrationModeState', 'status'), IMechanicState):

    def isTransition(self, other):
        return self.status != other.status

    @property
    def isPenBonusActive(self):
        return self.status & SHELL_CALIBRATION_STATE.PENETRATION_BONUS

    @property
    def isNonPenBonusActive(self):
        return self.status & SHELL_CALIBRATION_STATE.NON_PENETRATION_BONUS

    @property
    def isWaitingResult(self):
        return self.status & SHELL_CALIBRATION_STATE.WAITING_RESULT


class ShellCalibrationController(VehicleDynamicComponent, IGunMechanicComponent, IMechanicStatesComponent):

    def __init__(self):
        super(ShellCalibrationController, self).__init__()
        self.__mechanicPrefabSpawner = createMechanicPrefabSpawner(self.entity, self)
        self.__statesEvents = createMechanicStatesEvents(self)
        self.__calibrationShells = frozenset()
        self._initComponent()

    def set_status(self, _):
        self._updateComponentAppearance()
        self._updateComponentAvatar()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.SHELL_CALIBRATION

    @property
    def statesEvents(self):
        return self.__statesEvents

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = ShellCalibrationAmmoState(self.__calibrationShells)

    def getMechanicState(self):
        return ShellCalibrationModeState(self.status)

    def onDestroy(self):
        self.__statesEvents.destroy()
        super(ShellCalibrationController, self).onDestroy()

    def _onAppearanceReady(self):
        super(ShellCalibrationController, self)._onAppearanceReady()
        self.__statesEvents.processStatePrepared()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(ShellCalibrationController, self)._onComponentAppearanceUpdate(**kwargs)
        mechanicState = self.getMechanicState()
        self.__statesEvents.updateMechanicState(mechanicState)

    def _onComponentAvatarUpdate(self, player):
        super(ShellCalibrationController, self)._onComponentAvatarUpdate(player)
        player.updateVehicleAmmoStates()

    def _collectComponentParams(self, typeDescriptor):
        super(ShellCalibrationController, self)._collectComponentParams(typeDescriptor)
        mechanicParams = getVehicleDescrMechanicParams(typeDescriptor, self.vehicleMechanic)
        if mechanicParams is not None:
            self.__calibrationShells = frozenset((shot.shell.compactDescr for shot in typeDescriptor.gun.shots if shot.shell.compactDescr not in mechanicParams.forbiddenShells))
        else:
            self.__calibrationShells = frozenset()
        return
