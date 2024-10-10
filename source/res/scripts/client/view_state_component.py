# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/view_state_component.py
import weakref
import typing
from cache import cached_property
from constants import BuffDisplayedState
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_VIEW_STATE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MarkersManagerEvent
from helpers import dependency
from helpers.fixed_dict import getTimeInterval
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from helpers.fixed_dict import TimeInterval

class ViewStateComponent(DynamicScriptComponent):

    def __init__(self, *args, **kwargs):
        super(ViewStateComponent, self).__init__(*args, **kwargs)
        stateID = BuffDisplayedState(self.displayedState)
        self._viewStateUpdater = _viewStateUpdaterFactory(stateID=stateID, component=self)

    def onDestroy(self):
        if self._viewStateUpdater is not None:
            self._viewStateUpdater.destroy()
            self._viewStateUpdater = None
        super(ViewStateComponent, self).onDestroy()
        return

    def set_isActive(self, prev):
        if self._isAvatarReady:
            self._invalidateViewState()

    def set_timeInterval(self, prev):
        if self._isAvatarReady:
            self._invalidateViewState()

    def _onAvatarReady(self):
        self._invalidateViewState()

    def _invalidateViewState(self):
        if self._viewStateUpdater is not None:
            self._viewStateUpdater.invalidate()
        return


class ViewStateComponentAdaptor(object):

    def __init__(self, entity, state):
        self.__entity = weakref.proxy(entity)
        self.__state = state
        stateID = BuffDisplayedState(self.__state.stateID)
        self.__viewStateUpdater = _viewStateUpdaterFactory(stateID=stateID, component=self)
        self.__invalidateViewState()

    @property
    def entity(self):
        return self.__entity

    @property
    def isActive(self):
        return True

    @property
    def timeInterval(self):
        timeInterval = {'startTime': self.__state.timeInterval.startTime,
         'endTime': self.__state.timeInterval.endTime}
        return timeInterval

    @property
    def isSourceVehicle(self):
        return self.__state.isSourceVehicle

    def updateState(self, state):
        updated = False
        updated |= self.__state.timeInterval != state.timeInterval
        updated |= self.__state.isSourceVehicle != state.isSourceVehicle
        self.__state = state
        if updated:
            self.__invalidateViewState()

    def destroy(self):
        if self.__viewStateUpdater is not None:
            self.__viewStateUpdater.destroy()
            self.__viewStateUpdater = None
        return

    def __invalidateViewState(self):
        if self.__viewStateUpdater is not None:
            self.__viewStateUpdater.invalidate()
        return


class ViewStateUpdater(object):
    _FEEDBACK_EVENT_ID = None
    _VEHICLE_VIEW_STATE = None

    def __init__(self, component):
        self._component = weakref.proxy(component)
        self._vehicleID = self._component.entity.id
        self._isActive = self._component.isActive
        if self._vehicleStateCtrl:
            self._vehicleStateCtrl.onVehicleControlling += self.onVehicleControlling
        g_eventBus.addListener(MarkersManagerEvent.MARKERS_CREATED, self.invalidate, EVENT_BUS_SCOPE.BATTLE)

    @cached_property
    def _sessionProvider(self):
        return dependency.instance(IBattleSessionProvider)

    @cached_property
    def _vehicleStateCtrl(self):
        return self._sessionProvider.shared.vehicleState

    @property
    def _controllingVehicleID(self):
        return self._vehicleStateCtrl.getControllingVehicleID()

    def onVehicleControlling(self, vehicle):
        if self._vehicleID == vehicle.id:
            self.invalidate()

    def invalidate(self, _=None):
        isActive = self._component.isActive
        if isActive or self._isActive:
            self._isActive = isActive
            self._invalidateState()

    def destroy(self):
        self._component = None
        if self._isActive:
            self._isActive = False
            self._invalidateState()
        if self._vehicleStateCtrl:
            self._vehicleStateCtrl.onVehicleControlling -= self.onVehicleControlling
        g_eventBus.removeListener(MarkersManagerEvent.MARKERS_CREATED, self.invalidate, EVENT_BUS_SCOPE.BATTLE)
        return

    def _invalidateState(self):
        state = self._getState()
        if self._VEHICLE_VIEW_STATE is not None:
            if self._vehicleID == self._controllingVehicleID:
                self._sessionProvider.invalidateVehicleState(self._VEHICLE_VIEW_STATE, state)
        if self._FEEDBACK_EVENT_ID is not None:
            self._sessionProvider.shared.feedback.invalidateBuffEffect(self._FEEDBACK_EVENT_ID, self._vehicleID, state)
        return

    def _getState(self):
        if self._isActive:
            timeInterval = getTimeInterval(self._component.timeInterval)
            state = {'endTime': timeInterval.endTime,
             'duration': timeInterval.endTime - timeInterval.startTime}
        else:
            state = {'finishing': True}
        return state


def _viewStateUpdaterFactory(stateID, component):
    updater = _VIEW_STATE_UPDATERS.get(stateID)
    return updater(component) if updater is not None else None


class _AoeInspireStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_AOE_INSPIRE
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.AOE_INSPIRE

    def _getState(self):
        state = super(_AoeInspireStateUpdater, self)._getState()
        if self._isActive:
            state['isSourceVehicle'] = bool(self._component.isSourceVehicle)
        return state


class _AoeHealStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_AOE_HEAL
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.AOE_HEAL

    def _getState(self):
        state = super(_AoeHealStateUpdater, self)._getState()
        if self._isActive:
            state['isSourceVehicle'] = bool(self._component.isSourceVehicle)
        return state


class _RiskyAttackBuffStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_RISKY_ATTACK_BUFF
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.RISKY_ATTACK_BUFF


class _RiskyAttackHealStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_RISKY_ATTACK_HEAL
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.RISKY_ATTACK_HEAL


class _BerserkStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_BERSERK
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.BERSERK


class _SniperStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_SNIPER
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.SNIPER


class _HunterStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_HUNTER
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.HUNTER


class _FastRechargeStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_FAST_RECHARGE
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.FAST_RECHARGE


class _AllySupportStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_ALLY_SUPPORT
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.ALLY_SUPPORT


class _JuggernautStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_JUGGERNAUT
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.JUGGERNAUT


class _SureShotStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_SURE_SHOT
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.SURE_SHOT


class _ConcentrationStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_CONCENTRATION
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.CONCENTRATION


class _MarchStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_MARCH
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.MARCH


class _AggressiveDetectionStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.VEHICLE_AGGRESSIVE_DETECTION
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.AGGRESSIVE_DETECTION


class _AbilityStateUpdater(ViewStateUpdater):
    _FEEDBACK_EVENT_ID = FEEDBACK_EVENT_ID.ABILITY
    _VEHICLE_VIEW_STATE = VEHICLE_VIEW_STATE.ABILITY


_VIEW_STATE_UPDATERS = {BuffDisplayedState.AOE_INSPIRE: _AoeInspireStateUpdater,
 BuffDisplayedState.AOE_HEAL: _AoeHealStateUpdater,
 BuffDisplayedState.RISKY_ATTACK_BUFF: _RiskyAttackBuffStateUpdater,
 BuffDisplayedState.RISKY_ATTACK_HEAL: _RiskyAttackHealStateUpdater,
 BuffDisplayedState.BERSERK: _BerserkStateUpdater,
 BuffDisplayedState.SNIPER: _SniperStateUpdater,
 BuffDisplayedState.HUNTER: _HunterStateUpdater,
 BuffDisplayedState.FAST_RECHARGE: _FastRechargeStateUpdater,
 BuffDisplayedState.ALLY_SUPPORT: _AllySupportStateUpdater,
 BuffDisplayedState.JUGGERNAUT: _JuggernautStateUpdater,
 BuffDisplayedState.SURE_SHOT: _SureShotStateUpdater,
 BuffDisplayedState.CONCENTRATION: _ConcentrationStateUpdater,
 BuffDisplayedState.MARCH: _MarchStateUpdater,
 BuffDisplayedState.AGGRESSIVE_DETECTION: _AggressiveDetectionStateUpdater,
 BuffDisplayedState.ABILITY_JUGGERNAUT: _AbilityStateUpdater,
 BuffDisplayedState.ABILITY_CONCENTRATION: _AbilityStateUpdater,
 BuffDisplayedState.ABILITY_SURE_SHOT: _AbilityStateUpdater}
