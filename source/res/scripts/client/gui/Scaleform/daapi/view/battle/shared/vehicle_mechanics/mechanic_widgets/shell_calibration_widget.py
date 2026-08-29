# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/shell_calibration_widget.py
from __future__ import absolute_import
import typing
from ShellCalibrationController import ShellCalibrationModeState
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget
from gui.Scaleform.genConsts.SHELL_CALIBRATION_WIDGET_CONSTS import SHELL_CALIBRATION_WIDGET_CONSTS
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class ShellCalibrationMechanicWidget(VehicleMechanicWidget, ContainersListener, IMechanicStatesListenerLogic):

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateState(state, isInstantly=True)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__invalidateState(newState)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.SHELL_CALIBRATION, self), VehicleMechanicStatesUpdater(VehicleMechanic.SHELL_CALIBRATION, self)]

    def __invalidateState(self, state, isInstantly=False):
        widgetState = SHELL_CALIBRATION_WIDGET_CONSTS.NO_BONUS
        if state.isPenBonusActive:
            widgetState = SHELL_CALIBRATION_WIDGET_CONSTS.DAMAGE_BONUS
        elif state.isNonPenBonusActive:
            widgetState = SHELL_CALIBRATION_WIDGET_CONSTS.PENETRATION_BONUS
        self.as_setStateS(widgetState, isInstantly)
