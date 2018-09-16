# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleLTAchievement.py
from gui.shared.gui_items.dossier.achievements.ReadyForBattleAchievement import ReadyForBattleAchievement
from personal_missions import PM_BRANCH

class ReadyForBattleLTAchievement(ReadyForBattleAchievement):

    def __init__(self, dossier, value=None):
        super(ReadyForBattleLTAchievement, self).__init__(name='readyForBattleLT', classifier='lightTank', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)
