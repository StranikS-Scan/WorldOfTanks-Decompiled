# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/panels_common.py
import typing
from itertools import chain
import BattleReplay
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.battle_control.controllers.vehicle_passenger import VehiclePassengerInfoWatcher
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_info import getVehicleMechanics
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescr
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
    from Vehicle import Vehicle

def getMechanicsUIComponents(vehicleDescriptor, componentsMap):
    return chain((componentsMap[mechanic] for mechanic in getVehicleMechanics(vehicleDescriptor) if mechanic in componentsMap))


class VehicleMechanicsPanel(BaseDAAPIComponent, VehiclePassengerInfoWatcher):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {}

    def __init__(self):
        super(VehicleMechanicsPanel, self).__init__()
        self.__crosshairViewID = CROSSHAIR_VIEW_ID.UNDEFINED
        self.__isAllowedByContext = True

    def _populate(self):
        super(VehicleMechanicsPanel, self)._populate()
        self._setIsReplay(BattleReplay.g_replayCtrl.isPlaying)
        prebattleSetup = self.__sessionProvider.dynamic.prebattleSetup
        if prebattleSetup is not None:
            prebattleSetup.onBattleStarted += self.__onBattleStarted
            self.__updateContextAvailability()
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            self.__updateCrosshairViewID(crosshairCtrl.getViewID())
            crosshairCtrl.onCrosshairPositionChanged += self.__onCrosshairScaledPositionChanged
            crosshairCtrl.onCrosshairScaleChanged += self.__onCrosshairScaledPositionChanged
            self.__onCrosshairScaledPositionChanged()
        self.startVehiclePassengerLateListening(self._onVehicleControlling)
        self.__updateVisibility()
        return

    def _dispose(self):
        self.stopVehiclePassengerListening(self._onVehicleControlling)
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            crosshairCtrl.onCrosshairPositionChanged -= self.__onCrosshairScaledPositionChanged
            crosshairCtrl.onCrosshairScaleChanged -= self.__onCrosshairScaledPositionChanged
        prebattleSetup = self.__sessionProvider.dynamic.prebattleSetup
        if prebattleSetup is not None:
            prebattleSetup.onBattleStarted -= self.__onBattleStarted
        super(VehicleMechanicsPanel, self)._dispose()
        return

    def _setIsReplay(self, isReplay):
        raise NotImplementedError

    def _setIsVisible(self, isVisible):
        raise NotImplementedError

    def _setCrosshairScaledPosition(self, position):
        raise NotImplementedError

    def _setCrosshairViewID(self, viewID):
        raise NotImplementedError

    def _addMechanicUIComponent(self, mechanicComponent):
        raise NotImplementedError

    def _onVehicleControlling(self, vehicle):
        componentsMap = self._VEHICLE_MECHANIC_UI_COMPONENTS_MAP if vehicle is not None else {}
        for mechanicComponent in getMechanicsUIComponents(vehicle.typeDescriptor, componentsMap):
            self._addMechanicUIComponent(mechanicComponent)

        return

    def __onBattleStarted(self):
        self.__updateContextAvailability()
        self.__updateVisibility()

    def __onCrosshairScaledPositionChanged(self, *_):
        self._setCrosshairScaledPosition(self.__sessionProvider.shared.crosshair.getScaledPosition())

    def __onCrosshairViewChanged(self, viewID):
        self.__updateCrosshairViewID(viewID)
        self.__updateVisibility()

    def __updateContextAvailability(self):
        prebattleSetup = self.__sessionProvider.dynamic.prebattleSetup
        self.__isAllowedByContext = prebattleSetup is None or prebattleSetup.isVehicleStateIndicatorAllowed()
        return

    def __updateCrosshairViewID(self, viewID):
        self.__crosshairViewID = viewID
        self._setCrosshairViewID(viewID)

    def __updateVisibility(self):
        self._setIsVisible(self.__isAllowedByContext and self.__crosshairViewID not in (CROSSHAIR_VIEW_ID.UNDEFINED, CROSSHAIR_VIEW_ID.POSTMORTEM))
