# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleAllianceFrance.py
from gui.shared.gui_items.dossier.achievements.ReadyForBattleAchievement import ReadyForBattleAchievementSeason2
from nations import Alliances
from personal_missions import PM_BRANCH

class ReadyForBattleAllianceFranceAchievement(ReadyForBattleAchievementSeason2):

    def __init__(self, dossier, value=None):
        super(ReadyForBattleAllianceFranceAchievement, self).__init__(name='readyForBattleAllianceFrance', classifier=Alliances.FRANCE, branch=PM_BRANCH.PERSONAL_MISSION_2, dossier=dossier, value=value)
