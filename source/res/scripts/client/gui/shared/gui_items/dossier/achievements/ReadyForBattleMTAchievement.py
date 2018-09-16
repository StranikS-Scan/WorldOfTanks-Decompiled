# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleMTAchievement.py
from gui.shared.gui_items.dossier.achievements.ReadyForBattleAchievement import ReadyForBattleAchievement
from personal_missions import PM_BRANCH

class ReadyForBattleMTAchievement(ReadyForBattleAchievement):

    def __init__(self, dossier, value=None):
        super(ReadyForBattleMTAchievement, self).__init__(name='readyForBattleMT', classifier='mediumTank', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)
