# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/shared/tooltips/quests.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.quests import QuestsPreviewTooltipData
from gui.shared.formatters import text_styles
from gui.shared.tooltips.formatters import packImageTextBlockData, packPadding
from skeletons.gui.game_control import IWinbackController
from helpers import dependency
from winback.gui.Scaleform.daapi.view.tooltips.quests_block import getQuestTooltipBlock

class WinbackQuestsPreviewTooltipData(QuestsPreviewTooltipData):
    _MAX_QUESTS_PER_TOOLTIP = 3
    __winbackController = dependency.descriptor(IWinbackController)

    def _packBlocks(self, *args, **kwargs):
        items = []
        quests = self._getQuests()
        if quests:
            items.append(self._getHeader(len(quests), '', R.strings.tooltips.hangar.header.quests.description()))
            questsPerTooltip = min(len(quests), self._MAX_QUESTS_PER_TOOLTIP)
            items += [ getQuestTooltipBlock(quests[idx]) for idx in xrange(questsPerTooltip) ]
            rest = len(quests) - questsPerTooltip
            if rest > 0 and self._isShowBottom():
                items.append(self._getBottom(rest))
            if all((quest.isCompleted() for quest in quests)):
                items.append(self._getBody(backport.text(R.strings.tooltips.hangar.header.quests.empty())))
        return items

    def _getHeader(self, count, vehicleName, description):
        progressionName = self.__winbackController.progressionName
        title = backport.text(R.strings.winback.quests.tooltipHeader.dyn(progressionName)())
        img = backport.image(R.images.winback.gui.maps.icons.quests.tooltipHeader.dyn(progressionName)())
        desc = text_styles.main(backport.text(description))
        return packImageTextBlockData(title=text_styles.highTitle(title), img=img, txtPadding=packPadding(top=20), txtOffset=20, desc=desc)

    def _getQuests(self, *args):
        return sorted(self.__winbackController.winbackProgression.questContainer.getAvailableQuests().values(), key=lambda q: (q.isCompleted(), -q.getPriority(), q.getID()))

    def _isShowBottom(self, vehicle=None):
        return True
