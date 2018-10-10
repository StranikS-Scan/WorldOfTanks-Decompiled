# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic_random/score_panel.py
from gui.Scaleform.daapi.view.meta.EpicRandomScorePanelMeta import EpicRandomScorePanelMeta
from gui.battle_control.controllers.team_health_bar_ctrl import ITeamHealthBarListener
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class EpicRandomScorePanel(EpicRandomScorePanelMeta, ITeamHealthBarListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def updateTeamHealthPercent(self, allyPercentage, enemyPercentage):
        self.as_setTeamHealthPercentagesS(allyPercentage, enemyPercentage)
