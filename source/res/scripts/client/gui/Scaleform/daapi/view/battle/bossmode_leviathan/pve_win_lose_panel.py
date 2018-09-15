# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/pve_win_lose_panel.py
import BigWorld
from helpers import dependency, i18n
from gui.Scaleform.daapi.view.meta.PvEWinLosePanelMeta import PvEWinLosePanelMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from PlayerEvents import g_playerEvents
_TITLE = 0
_ICON_MESSAGE = 1
_BOTTOM_MESSAGE = 2
_PLAYER_TEAM_NUMBER = 1

class PvEWinLosePanel(PvEWinLosePanelMeta):

    def __init__(self):
        super(PvEWinLosePanel, self).__init__()
        self.__winText = (INGAME_GUI.HALLOWEEN_PVE_VICTORY_PANEL_TITLE, INGAME_GUI.HALLOWEEN_PVE_VICTORY_PANEL_ICONMESSAGE, INGAME_GUI.HALLOWEEN_PVE_VICTORY_PANEL_COMMENTARY)
        self.__defeatText = (INGAME_GUI.HALLOWEEN_PVE_DEFEAT_PANEL_TITLE, INGAME_GUI.HALLOWEEN_PVE_DEFEAT_PANEL_ICONMESSAGE, INGAME_GUI.HALLOWEEN_PVE_DEFEAT_PANEL_COMMENTARY)

    def _dispose(self):
        super(PvEWinLosePanel, self)._dispose()
        g_playerEvents.onRoundFinished -= self.__onRoundFinished

    def _populate(self):
        super(PvEWinLosePanel, self)._populate()
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def __submitEndingMessage(self, isWin):
        if isWin:
            msgs = self.__winText
        else:
            msgs = self.__defeatText
        vo = {'iWin': isWin,
         'title': i18n.makeString(msgs[_TITLE]),
         'iconText': i18n.makeString(msgs[_ICON_MESSAGE]),
         'bottomText': i18n.makeString(msgs[_BOTTOM_MESSAGE])}
        self.as_setCombatEndStateS(vo)

    def __onRoundFinished(self, winnerTeam, reason):
        playersWon = winnerTeam == _PLAYER_TEAM_NUMBER
        self.__submitEndingMessage(isWin=playersWon)
