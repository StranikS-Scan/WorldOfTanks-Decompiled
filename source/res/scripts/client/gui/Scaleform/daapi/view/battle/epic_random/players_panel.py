# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic_random/players_panel.py
from account_helpers.settings_core.settings_constants import GAME
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel
from gui.Scaleform.genConsts.EPIC_RANDOM_PLAYERS_PANEL_STATE import EPIC_RANDOM_PLAYERS_PANEL_STATE
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE = (EPIC_RANDOM_PLAYERS_PANEL_STATE.HIDDEN,
 EPIC_RANDOM_PLAYERS_PANEL_STATE.SHORT,
 EPIC_RANDOM_PLAYERS_PANEL_STATE.MEDIUM_PLAYER,
 EPIC_RANDOM_PLAYERS_PANEL_STATE.MEDIUM_TANK,
 EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_HIDDEN,
 EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_SHORT,
 EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_MEDIUM_PLAYER,
 EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_MEDIUM_TANK)

class EpicPlayerPanelStateSetting(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def read(cls):
        state = cls.settingsCore.getSetting(GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE)
        if state in _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE:
            return state
        else:
            return EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_SHORT

    @classmethod
    def write(cls, state):
        if state in _EPIC_RANDOM_PLAYERS_PANEL_STATE_RANGE:
            cls.settingsCore.applySetting(GAME.EPIC_RANDOM_PLAYERS_PANELS_STATE, state)
            return True
        else:
            LOG_ERROR('State of players panel is invalid', state)
            return False


class EpicRandomPlayersPanel(PlayersPanel):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self._mode = EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_SHORT

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
        self.as_setPanelModeS(EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_MEDIUM_PLAYER)

    def _handleNextMode(self, _):
        mode = (self._mode + 1) % (EPIC_RANDOM_PLAYERS_PANEL_STATE.TOGGLED_MEDIUM_TANK + 1)
        if EpicPlayerPanelStateSetting.write(mode):
            self._mode = mode
            self.as_setPanelModeS(mode)
