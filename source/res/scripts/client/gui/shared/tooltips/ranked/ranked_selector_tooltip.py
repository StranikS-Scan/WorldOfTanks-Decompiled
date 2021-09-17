# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_selector_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.periodic.prime_helpers import getPrimeTableBlocks
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 280

class RankedSelectorTooltip(BlocksTooltipData):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    _battleController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx):
        super(RankedSelectorTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_SELECTOR_INFO)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(RankedSelectorTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        items.append(self._packTimeTableBlock())
        items.append(self._getTillEndBlock(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self._battleController.getCurrentSeason().getCycleEndDate()))))
        return items

    def _packHeaderBlock(self):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.selectorTooltip.title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.selectorTooltip.desc())))

    def _packTimeTableBlock(self, leftPadding=0):
        primeTime = self._battleController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
        currentCycleEnd = self._battleController.getCurrentSeason().getCycleEndDate()
        return formatters.packBuildUpBlockData(getPrimeTableBlocks(primeTime, currentCycleEnd, R.strings.ranked_battles.selectorTooltip), 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=leftPadding))

    def _getTillEndBlock(self, timeLeft):
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.ranked_battles.selectorTooltip.tillEnd())) + ' ' + text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.ranked.availability)))


class RankedUnavailableTooltip(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(RankedUnavailableTooltip, self).__init__(context, None)
        self._setWidth(540)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(RankedUnavailableTooltip, self)._packBlocks(*args, **kwargs)
        tooltipData = R.strings.tooltips.battleTypes.ranked
        header = backport.text(tooltipData.header())
        body = backport.text(tooltipData.body())
        nextSeason = self.rankedController.getNextSeason()
        if self.rankedController.isFrozen() and self.rankedController.getCurrentSeason() is not None:
            additionalInfo = backport.text(tooltipData.body.frozen())
        elif nextSeason is not None:
            date = backport.getShortDateFormat(time_utils.makeLocalServerTime(nextSeason.getStartDate()))
            additionalInfo = backport.text(tooltipData.body.coming(), date=date)
        else:
            additionalInfo = backport.text(tooltipData.body.disabled())
        body = '%s\n\n%s' % (body, additionalInfo)
        items.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(header), desc=text_styles.main(body)))
        return items
