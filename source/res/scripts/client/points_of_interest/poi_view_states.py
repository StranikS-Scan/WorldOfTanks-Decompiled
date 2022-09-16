# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/poi_view_states.py
from collections import namedtuple
import typing
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

    def __init__(self, state):
        self._state = state
        self.__viewState = None
        return

    @property
    def state(self):
        return self._state

    def update(self):
        if self._state is None:
            return
        else:
            viewState = self._getViewState(self._state)
            if viewState != self.__viewState:
                self.__viewState = viewState
                self.__invalidateViewState()
            return

    def clear(self):
        self._state = None
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
