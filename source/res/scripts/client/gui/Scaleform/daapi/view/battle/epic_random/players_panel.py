# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic_random/players_panel.py
from account_helpers.settings_core.settings_constants import GAME
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.EpicRandomPlayersPanelMeta import EpicRandomPlayersPanelMeta
from gui.Scaleform.genConsts.PLAYERS_PANEL_STATE import PLAYERS_PANEL_STATE
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE = (PLAYERS_PANEL_STATE.HIDDEN,
 PLAYERS_PANEL_STATE.SHORT,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_SINGLE_COLUMN_MEDIUM_PLAYER,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_SINGLE_COLUMN_MEDIUM_TANK,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_HIDDEN,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK)
_EPIC_RANDOM_PLAYERS_PANEL_MULTI_COLUMN_STATE_RANGE = (PLAYERS_PANEL_STATE.HIDDEN,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT_SECOND_FOCUS,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER_SECOND_FOCUS,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK_SECOND_FOCUS,
 PLAYERS_PANEL_STATE.HIDDEN,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT_THIRD_FOCUS,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER_THIRD_FOCUS,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK_THIRD_FOCUS)
_EPIC_RANDOM_MULTI_COLUMN_TO_STATE = {0: {0: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT,
     1: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT_SECOND_FOCUS,
     2: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT_THIRD_FOCUS},
 1: {0: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER,
     1: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER_SECOND_FOCUS,
     2: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER_THIRD_FOCUS},
 2: {0: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK,
     1: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK_SECOND_FOCUS,
     2: PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK_THIRD_FOCUS},
 3: {}}
_EPIC_RANDOM_BUTTON_STATE_TO_MODE = {PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT: 0,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER: 1,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK: 2,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT_SECOND_FOCUS: 0,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER_SECOND_FOCUS: 1,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK_SECOND_FOCUS: 2,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT_THIRD_FOCUS: 0,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER_THIRD_FOCUS: 1,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_TANK_THIRD_FOCUS: 2,
 PLAYERS_PANEL_STATE.HIDDEN: 3}

class EpicPlayerPanelStateSetting(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def read(cls):
        state = cls.settingsCore.getSetting(GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE)
        return state if state in _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE else PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT

    @classmethod
    def write(cls, state):
        if state in _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE:
            cls.settingsCore.applySetting(GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE, state)
            return True
        LOG_ERROR('State of players panel is invalid', state)
        return False


class EpicRandomPlayersPanel(EpicRandomPlayersPanelMeta):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicRandomPlayersPanel, self).__init__()
        self._mode = PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_SHORT
        self.__focusedColumn = 0
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        return

    def _dispose(self):
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        super(EpicRandomPlayersPanel, self)._dispose()
        return

    def focusedColumnChanged(self, value):
        buttonMode = _EPIC_RANDOM_BUTTON_STATE_TO_MODE[self._mode]
        mode = _EPIC_RANDOM_MULTI_COLUMN_TO_STATE[buttonMode][value]
        self.__focusedColumn = value
        self._mode = mode
        self.as_setPanelModeS(mode)

    def tryToSetPanelModeByMouse(self, mode):
        if mode == PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_HIDDEN or mode not in PLAYERS_PANEL_STATE.EXTENDED_STATES:
            self.__focusedColumn = 0
        newMode = mode
        if self.__focusedColumn != 0:
            buttonMode = _EPIC_RANDOM_BUTTON_STATE_TO_MODE[newMode]
            newMode = _EPIC_RANDOM_MULTI_COLUMN_TO_STATE[buttonMode][self.__focusedColumn]
        if newMode != self._mode:
            self._mode = newMode
            self.as_setPanelModeS(newMode)
            EpicPlayerPanelStateSetting.write(newMode)

    def switchToOtherPlayer(self, vehicleID):
        self.guiSessionProvider.shared.viewPoints.selectVehicle(int(vehicleID))

    def setInitialMode(self):
        self.__focusedColumn = 0
        self._mode = EpicPlayerPanelStateSetting.read()
        self.as_setPanelModeS(self._mode)

    def setLargeMode(self):
        self.as_setPanelModeS(PLAYERS_PANEL_STATE.EPIC_RANDOM_THREE_COLUMN_MEDIUM_PLAYER)

    def _handleNextMode(self, _):
        mode = PLAYERS_PANEL_STATE.HIDDEN
        if self.__focusedColumn != 0:
            index = (_EPIC_RANDOM_PLAYERS_PANEL_MULTI_COLUMN_STATE_RANGE.index(self._mode) + 1) % len(_EPIC_RANDOM_PLAYERS_PANEL_MULTI_COLUMN_STATE_RANGE)
            mode = _EPIC_RANDOM_PLAYERS_PANEL_MULTI_COLUMN_STATE_RANGE[index]
            if mode == PLAYERS_PANEL_STATE.HIDDEN:
                self.__focusedColumn = 0
        else:
            index = (_EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE.index(self._mode) + 1) % len(_EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE)
            mode = _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE[index]
        if self.__focusedColumn != 0 or EpicPlayerPanelStateSetting.write(mode):
            self._mode = mode
            self.as_setPanelModeS(mode)

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.as_setPlayersSwitchingAllowedS(True)

    def __onRespawnBaseMoving(self):
        self.as_setPlayersSwitchingAllowedS(False)
