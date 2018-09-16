# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/ReadyForBattleSPGAchievement.py
from gui.shared.gui_items.dossier.achievements.ReadyForBattleAchievement import ReadyForBattleAchievement
from personal_missions import PM_BRANCH

class ReadyForBattleSPGAchievement(ReadyForBattleAchievement):

    def __init__(self, dossier, value=None):
        super(ReadyForBattleSPGAchievement, self).__init__(name='readyForBattleSPG', classifier='SPG', branch=PM_BRANCH.REGULAR, dossier=dossier, value=value)
