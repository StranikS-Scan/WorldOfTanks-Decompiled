# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_players_panel.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayerPanelStateSetting
from gui.Scaleform.daapi.view.meta.FootballPlayersPanelMeta import FootballPlayersPanelMeta
from gui.Scaleform.genConsts.PLAYERS_PANEL_STATE import PLAYERS_PANEL_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView

class FootballPlayerPanelStateSetting(PlayerPanelStateSetting):
    pass


class PlayersPanel(FootballPlayersPanelMeta, IAbstractPeriodView):

    def setLargeMode(self):
        self.as_setPanelModeS(PLAYERS_PANEL_STATE.MEDIUM)
