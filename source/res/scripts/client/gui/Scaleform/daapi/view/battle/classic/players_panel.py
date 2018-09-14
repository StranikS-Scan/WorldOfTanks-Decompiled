# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/players_panel.py
from account_helpers.settings_core import g_settingsCore
from gui.Scaleform.daapi.view.meta.PlayersPanelMeta import PlayersPanelMeta
from gui.Scaleform.genConsts.PLAYERS_PANEL_STATE import PLAYERS_PANEL_STATE
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.period_ctrl import IPlayersPanelsSwitcher
from gui.shared import events, EVENT_BUS_SCOPE
_LEGACY_TO_NEW_MODE = {'hidden': PLAYERS_PANEL_STATE.HIDEN,
 'short': PLAYERS_PANEL_STATE.SHORT,
 'medium': PLAYERS_PANEL_STATE.MEDIUM,
 'medium2': PLAYERS_PANEL_STATE.LONG,
 'large': PLAYERS_PANEL_STATE.FULL}
_NEW_TO_LEGACY_MODE = dict(((v, k) for k, v in _LEGACY_TO_NEW_MODE.iteritems()))

def _getNewModeFromSetting():
    state = g_settingsCore.getSetting('ppState')
    if state in _LEGACY_TO_NEW_MODE:
        converted = _LEGACY_TO_NEW_MODE[state]
    else:
        converted = _LEGACY_TO_NEW_MODE['large']
    return converted


def _writeSettingFromNewMode(mode):
    if mode in _NEW_TO_LEGACY_MODE:
        state = _NEW_TO_LEGACY_MODE[mode]
        g_settingsCore.applySetting('ppState', state)
        return True
    else:
        return False


class PlayersPanel(PlayersPanelMeta, IPlayersPanelsSwitcher):

    def __init__(self):
        super(PlayersPanel, self).__init__()
        self.__mode = PLAYERS_PANEL_STATE.FULL

    def tryToSetPanelModeByMouse(self, mode):
        if mode != self.__mode and _writeSettingFromNewMode(mode):
            self.__mode = mode
            self.as_setPanelModeS(mode)

    def switchToOtherPlayer(self, vehicleID):
        avatar_getter.switchToOtherPlayer(int(vehicleID))

    def setInitialMode(self):
        self.as_setPanelModeS(self.__mode)

    def setLargeMode(self):
        self.as_setPanelModeS(PLAYERS_PANEL_STATE.FULL)

    def _populate(self):
        self.__mode = _getNewModeFromSetting()
        super(PlayersPanel, self)._populate()
        self.addListener(events.GameEvent.NEXT_PLAYERS_PANEL_MODE, self.__handleNextMode, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.NEXT_PLAYERS_PANEL_MODE, self.__handleNextMode, EVENT_BUS_SCOPE.BATTLE)
        super(PlayersPanel, self)._dispose()

    def __handleNextMode(self, _):
        mode = (self.__mode + 1) % (PLAYERS_PANEL_STATE.FULL + 1)
        if _writeSettingFromNewMode(mode):
            self.__mode = mode
            self.as_setPanelModeS(mode)
