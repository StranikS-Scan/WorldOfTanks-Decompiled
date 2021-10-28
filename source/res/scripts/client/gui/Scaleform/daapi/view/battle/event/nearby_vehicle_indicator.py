# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/nearby_vehicle_indicator.py
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from wotdecorators import condition
from gui.Scaleform.daapi.view.meta.PveBossIndicatorProgressMeta import PveBossIndicatorProgressMeta
from game_event_getter import GameEventGetterMixin
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.server_events.game_event.difficulty_progress import DifficultyLevelItem
from skeletons.gui.game_event_controller import IGameEventController
_NORMAL_ENVIRONMENT_ID = 0
_MAX_UI_INDICATOR_VALUE = 100

class NearByVehicleIndicator(PveBossIndicatorProgressMeta, GameEventGetterMixin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    gameEventController = dependency.descriptor(IGameEventController)
    ifEnabled = condition('_isEnabled')

    def __init__(self):
        super(NearByVehicleIndicator, self).__init__()
        self.__isVisible = True
        self.__currentVehicleID = avatar_getter.getPlayerVehicleID()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    @property
    def _isEnabled(self):
        envsList = self.environmentData.getEnvironmentsList()
        currentDifficultyLevel = self.gameEventController.getSelectedDifficultyLevel()
        return False if self.environmentData.getCurrentEnvironmentID() == envsList[0]['id'] and currentDifficultyLevel == DifficultyLevelItem.EASY else True

    def toggle(self, isShown):
        self.__isVisible = isShown
        if self._isEnabled:
            self.as_setIndicatorEnabledS(isShown)

    def show(self, isVisible):
        self.__isVisible = isVisible
        if self._isEnabled:
            self.as_setIndicatorEnabledS(self.__isVisible)

    def _populate(self):
        super(NearByVehicleIndicator, self)._populate()
        if self.environmentData is not None:
            self.environmentData.onUpdated += self._update
        if self.nearbyIndicatorData is not None:
            self.nearbyIndicatorData.onUpdated += self._update
        self._update()
        return

    def _dispose(self):
        super(NearByVehicleIndicator, self)._dispose()
        if self.environmentData is not None:
            self.environmentData.onUpdated -= self._update
        if self.nearbyIndicatorData is not None:
            self.nearbyIndicatorData.onUpdated -= self._update
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return

    @ifEnabled
    def _update(self):
        self.show(self.__isVisible)
        self.as_setValueS(min(self._getIndicatorValue(), _MAX_UI_INDICATOR_VALUE))

    def _getIndicatorValue(self):
        return 0 if self.nearbyIndicatorData is None else self.nearbyIndicatorData.getIndicatorValue(str(self.__currentVehicleID))

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.PLAYER_INFO and self.__currentVehicleID != value:
            self.__currentVehicleID = value
            self._update()
