# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/vehicle_mechanics/widgets_presenter.py
from __future__ import absolute_import
import typing
from future.utils import viewitems, viewvalues
from events_handler import eventHandler
from gui.battle_control.controllers.vehicle_passenger import hasVehiclePassengerCtrl, VehiclePassengerInfoWatcher
from gui.impl.pub.view_component import ViewComponent
from gui.veh_mechanics.battle.updaters.mechanics.tracked_mechanics_updater import IVehicleTrackedMechanicsView, VehicleTrackedMechanicsUpdater
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdatersCollection
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from items.vehicle_mechanics_types import VehicleMechanicKey
_WIDGET_ALIASES_BY_MECHANIC = {}

class VisibilityState(object):
    DEFAULT = 0
    IN_POSTMORTEM = 1

    @staticmethod
    def validate(state, value):
        return False if state & VisibilityState.IN_POSTMORTEM else value


class VehicleMechanicsWidgetsPresenter(ViewComponent, VehiclePassengerInfoWatcher, IVehicleTrackedMechanicsView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VehicleMechanicsWidgetsPresenter, self).__init__()
        self.__updatersCollection = ViewUpdatersCollection()
        self.__visibilityState = VisibilityState.DEFAULT

    @eventHandler
    def onTrackedMechanicsUpdate(self, mechanics):
        trackedMechanics = set(mechanics)
        for mechanic, resIds in viewitems(_WIDGET_ALIASES_BY_MECHANIC):
            isTracked = mechanic in trackedMechanics
            for resId in resIds:
                self.__enableComponent(isTracked, resId)

    @property
    def viewModel(self):
        return super(VehicleMechanicsWidgetsPresenter, self).getViewModel()

    def _getChildComponents(self):
        pass

    def _getEvents(self):
        vehicleCtrl = self.__sessionProvider.shared.vehicleState
        return () if vehicleCtrl is None else ((vehicleCtrl.onPostMortemSwitched, self.__onSwitchToPostmortem),)

    def _onLoaded(self, *args, **kwargs):
        super(VehicleMechanicsWidgetsPresenter, self)._onLoaded(*args, **kwargs)
        self.__updatersCollection.initialize([VehicleTrackedMechanicsUpdater(self)])
        self.startVehiclePassengerLateListening(self.__onVehicleControlling)

    def _finalize(self):
        self.stopVehiclePassengerListening(self.__onVehicleControlling)
        self.__updatersCollection.finalize()
        self.__visibilityState = VisibilityState.DEFAULT
        super(VehicleMechanicsWidgetsPresenter, self)._finalize()

    @hasVehiclePassengerCtrl()
    def __onVehicleControlling(self, _, passengerCtrl=None):
        pass

    def __onSwitchToPostmortem(self, _, __):
        self.__visibilityState |= VisibilityState.IN_POSTMORTEM
        for resIds in viewvalues(_WIDGET_ALIASES_BY_MECHANIC):
            for resId in resIds:
                self.__enableComponent(False, resId)

    def __enableComponent(self, value, resId):
        value = VisibilityState.validate(self.__visibilityState, value)
        child = self.getChildByPosId(resId)
        if child is None:
            if value:
                self._constructChild(resId)
        else:
            child.setEnabled(value)
        return
