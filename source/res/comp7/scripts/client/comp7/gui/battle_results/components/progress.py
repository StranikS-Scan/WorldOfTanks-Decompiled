# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_results/components/progress.py
from gui.battle_results.components.progress import BattlePassProgressBlock
from gui.impl import backport
from gui.impl.gen import R
_POST_BATTLE_RES = R.strings.battle_pass.reward.postBattle

class Comp7BattlePassProgressBlock(BattlePassProgressBlock):

    @staticmethod
    def _getDescription(progress):
        if progress.pointsAux:
            text = backport.text(_POST_BATTLE_RES.progress.pointsAux())
        else:
            text = backport.text(_POST_BATTLE_RES.comp7.progress())
        return text

    @staticmethod
    def _getProgressDiffTooltip(progress, chapterID):
        return backport.text(_POST_BATTLE_RES.comp7.progress.tooltip(), points=progress.getPointsDiff(chapterID))
