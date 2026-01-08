# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/panels_common.py
from __future__ import absolute_import
import typing
from itertools import chain
import BattleReplay
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
from gui.veh_mechanics.battle.updaters.mechanics.tracked_mechanics_updater import IVehicleTrackedMechanicsView, VehicleTrackedMechanicsUpdater
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdatersCollection
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

def getMechanicsUIComponents(vehicleMechanics, componentsMap):
    return chain((componentsMap[mechanic] for mechanic in vehicleMechanics if mechanic in componentsMap))


class VehicleMechanicsPanel(BaseDAAPIComponent, ContainersListener, IVehicleTrackedMechanicsView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {}

    def __init__(self):
        super(VehicleMechanicsPanel, self).__init__()
        self.__updatersCollection = ViewUpdatersCollection()
        self.__crosshairViewID = CROSSHAIR_VIEW_ID.UNDEFINED
        self.__isAllowedByContext = True

    @eventHandler
    def onTrackedMechanicsUpdate(self, mechanics):
        for mechanicComponent in getMechanicsUIComponents(mechanics, self._VEHICLE_MECHANIC_UI_COMPONENTS_MAP):
            self._addMechanicUIComponent(mechanicComponent)

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
        self.__updatersCollection.initialize([VehicleTrackedMechanicsUpdater(self)])
        self.__updateVisibility()
        return

    def _dispose(self):
        self.__updatersCollection.finalize()
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

    def _destroy(self):
        self.__updatersCollection.destroy()
        super(VehicleMechanicsPanel, self)._destroy()

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
        isValidCrosshairID = self.__crosshairViewID not in (CROSSHAIR_VIEW_ID.UNDEFINED, CROSSHAIR_VIEW_ID.POSTMORTEM)
        self._setIsVisible(isValidCrosshairID and self.__isAllowedByContext)
