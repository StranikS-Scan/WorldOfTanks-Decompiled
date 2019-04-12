# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_battles_division_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 364
_TOOLTIP_ICON_SIZE = 56

class RankedDivisionTooltip(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx):
        super(RankedDivisionTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_DIVISION_INFO)
        self._setContentMargin(top=18, left=20, bottom=18, right=20)
        self._setMargins(afterBlock=13)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, divisionId, isCurrent, isLocked, isCompleted):
        items = super(RankedDivisionTooltip, self)._packBlocks()
        division = findFirst(lambda d: d.getUserID() == divisionId, self.rankedController.getDivisions())
        divisionIcon = backport.image(R.images.gui.maps.icons.rankedBattles.divisions.c_56x56.dyn(divisionId)())
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.division.dyn(divisionId)())), desc=text_styles.main(backport.text(R.strings.ranked_battles.division.tooltip.rankDescription(), ranksCount=len(division.getRanksIDs()))), img=divisionIcon, imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10)))
        descTitle = text_styles.middleTitle(backport.text(R.strings.ranked_battles.division.tooltip.desc.title()))
        descText = text_styles.standard(backport.text(R.strings.ranked_battles.division.tooltip.desc.current.text()))
        statusTitle = text_styles.warning(backport.text(R.strings.ranked_battles.division.tooltip.status.current()))
        statusText = text_styles.standard(backport.text(R.strings.ranked_battles.division.tooltip.status.locked.desc()))
        if isLocked:
            descText = text_styles.standard(backport.text(R.strings.ranked_battles.division.tooltip.desc.locked.text()))
            statusTitle = text_styles.critical(backport.text(R.strings.ranked_battles.division.tooltip.status.locked()))
        elif isCompleted:
            descText = text_styles.standard(backport.text(R.strings.ranked_battles.division.tooltip.desc.completed.text()))
            statusTitle = text_styles.statInfo(backport.text(R.strings.ranked_battles.division.tooltip.status.completed()))
        items.append(formatters.packImageTextBlockData(title=descTitle, desc=descText, txtPadding=formatters.packPadding(left=10)))
        items.append(formatters.packImageTextBlockData(title=statusTitle, desc=statusText if isLocked else None, txtPadding=formatters.packPadding(left=10)))
        return items
