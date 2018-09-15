# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic_random/players_panel.py
from account_helpers.settings_core.settings_constants import GAME
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel
from gui.Scaleform.genConsts.PLAYERS_PANEL_STATE import PLAYERS_PANEL_STATE
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE = (PLAYERS_PANEL_STATE.HIDDEN,
 PLAYERS_PANEL_STATE.SHORT,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_MEDIUM_PLAYER,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_MEDIUM_TANK,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_TOGGLED_HIDDEN,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_TOGGLED_SHORT,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_TOGGLED_MEDIUM_PLAYER,
 PLAYERS_PANEL_STATE.EPIC_RANDOM_TOGGLED_MEDIUM_TANK)

class EpicPlayerPanelStateSetting(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def read(cls):
        state = cls.settingsCore.getSetting(GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE)
        return state if state in _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE else PLAYERS_PANEL_STATE.EPIC_RANDOM_TOGGLED_SHORT

    @classmethod
    def write(cls, state):
        if state in _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE:
            cls.settingsCore.applySetting(GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE, state)
            return True
        LOG_ERROR('State of players panel is invalid', state)
        return False


class EpicRandomPlayersPanel(PlayersPanel):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self._mode = PLAYERS_PANEL_STATE.EPIC_RANDOM_TOGGLED_SHORT

    def tryToSetPanelModeByMouse(self, mode):
        if mode != self._mode and EpicPlayerPanelStateSetting.write(mode):
            self._mode = mode
            self.as_setPanelModeS(mode)

    def switchToOtherPlayer(self, vehicleID):
        self.guiSessionProvider.shared.viewPoints.selectVehicle(int(vehicleID))

    def setInitialMode(self):
        self._mode = EpicPlayerPanelStateSetting.read()
        self.as_setPanelModeS(self._mode)

    def setLargeMode(self):
        self.as_setPanelModeS(PLAYERS_PANEL_STATE.EPIC_RANDOM_TOGGLED_MEDIUM_PLAYER)

    def _handleNextMode(self, _):
        index = (_EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE.index(self._mode) + 1) % len(_EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE)
        mode = _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE[index]
        if EpicPlayerPanelStateSetting.write(mode):
            self._mode = mode
            self.as_setPanelModeS(mode)
