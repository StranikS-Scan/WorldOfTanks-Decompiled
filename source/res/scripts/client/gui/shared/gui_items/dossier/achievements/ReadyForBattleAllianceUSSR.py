# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleAllianceUSSR.py
from gui.shared.gui_items.dossier.achievements.ReadyForBattleAchievement import ReadyForBattleAchievementSeason2
from nations import Alliances
from personal_missions import PM_BRANCH

class ReadyForBattleAllianceUSSRAchievement(ReadyForBattleAchievementSeason2):

    def __init__(self, dossier, value=None):
        super(ReadyForBattleAllianceUSSRAchievement, self).__init__(name='readyForBattleAllianceUSSR', classifier=Alliances.USSR, branch=PM_BRANCH.PERSONAL_MISSION_2, dossier=dossier, value=value)
