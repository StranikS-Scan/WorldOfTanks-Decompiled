# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/poi_view_states.py
from collections import namedtuple
import typing
import CGF
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
PointViewState = namedtuple('PointState', ('id', 'type', 'status', 'invader'))
VehicleViewState = namedtuple('VehicleState', ('id', 'blockReasons'))
if typing.TYPE_CHECKING:
    from points_of_interest.components import PoiStateComponent, PoiCaptureBlockerStateComponent
    StateComponent = typing.Union[PoiStateComponent, PoiCaptureBlockerStateComponent]
    ViewState = typing.Union[PointViewState, VehicleViewState]

class _ViewStateUpdater(object):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, stateUUID):
        self.__stateUUID = stateUUID
        self.__viewState = None
        return

    def getState(self, statesAccess):
        return statesAccess.find(self.__stateUUID)

    def update(self, statesAccess):
        state = self.getState(statesAccess)
        if state is None:
            return
        else:
            viewState = self._getViewState(state)
            if viewState != self.__viewState:
                self.__viewState = viewState
                self.__invalidateViewState()
            return

    def clear(self):
        self.__viewState = None
        self.__invalidateViewState()
        return

    @staticmethod
    def _getViewStateID():
        raise NotImplementedError

    @staticmethod
    def _getViewState(state):
        raise NotImplementedError

    def __invalidateViewState(self):
        self.__guiSessionProvider.invalidateVehicleState(self._getViewStateID(), self.__viewState)


class PointViewStateUpdater(_ViewStateUpdater):

    @staticmethod
    def _getViewStateID():
        from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
        return VEHICLE_VIEW_STATE.POINT_OF_INTEREST_STATE

    @staticmethod
    def _getViewState(state):
        viewState = PointViewState(id=state.id, type=state.type, status=state.status, invader=state.invader)
        return viewState


class VehicleViewStateUpdater(_ViewStateUpdater):

    @staticmethod
    def _getViewStateID():
        from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
        return VEHICLE_VIEW_STATE.POINT_OF_INTEREST_VEHICLE_STATE

    @staticmethod
    def _getViewState(state):
        viewState = VehicleViewState(id=state.id, blockReasons=state.blockReasons)
        return viewState
