# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/players_panel.py
from account_helpers.settings_core.settings_constants import GAME
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.PlayersPanelMeta import PlayersPanelMeta
from gui.Scaleform.genConsts.PLAYERS_PANEL_STATE import PLAYERS_PANEL_STATE
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.period_ctrl import IPlayersPanelsSwitcher
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_PLAYERS_PANEL_STATE_RANGE = (PLAYERS_PANEL_STATE.HIDEN,
 PLAYERS_PANEL_STATE.SHORT,
 PLAYERS_PANEL_STATE.MEDIUM,
 PLAYERS_PANEL_STATE.LONG,
 PLAYERS_PANEL_STATE.FULL)

class PlayerPanelStateSetting(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    @classmethod
    def read(cls):
        state = cls.settingsCore.getSetting(GAME.PLAYERS_PANELS_STATE)
        if state in _PLAYERS_PANEL_STATE_RANGE:
            return state
        else:
            return PLAYERS_PANEL_STATE.MEDIUM

    @classmethod
    def write(cls, state):
        if state in _PLAYERS_PANEL_STATE_RANGE:
            cls.settingsCore.applySetting(GAME.PLAYERS_PANELS_STATE, state)
            return True
        else:
            LOG_ERROR('State of players panel is invalid', state)
            return False


class PlayersPanel(PlayersPanelMeta, IPlayersPanelsSwitcher):

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self.__mode = PLAYERS_PANEL_STATE.FULL

    def tryToSetPanelModeByMouse(self, mode):
        if mode != self.__mode and PlayerPanelStateSetting.write(mode):
            self.__mode = mode
            self.as_setPanelModeS(mode)

    def switchToOtherPlayer(self, vehicleID):
        avatar_getter.switchToOtherPlayer(int(vehicleID))

    def setInitialMode(self):
        self.__mode = PlayerPanelStateSetting.read()
        self.as_setPanelModeS(self.__mode)

    def setLargeMode(self):
        self.as_setPanelModeS(PLAYERS_PANEL_STATE.FULL)

    def _populate(self):
        super(PlayersPanel, self)._populate()
        self.addListener(events.GameEvent.NEXT_PLAYERS_PANEL_MODE, self.__handleNextMode, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.NEXT_PLAYERS_PANEL_MODE, self.__handleNextMode, EVENT_BUS_SCOPE.BATTLE)
        super(PlayersPanel, self)._dispose()

    def __handleNextMode(self, _):
        mode = (self.__mode + 1) % (PLAYERS_PANEL_STATE.FULL + 1)
        if PlayerPanelStateSetting.write(mode):
            self.__mode = mode
            self.as_setPanelModeS(mode)
