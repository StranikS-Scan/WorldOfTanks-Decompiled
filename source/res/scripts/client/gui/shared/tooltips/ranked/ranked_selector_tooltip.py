# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_selector_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.battle_selector import SeasonalBattleSelectorTooltip
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 280

class RankedSelectorTooltip(SeasonalBattleSelectorTooltip):
    _battleController = dependency.descriptor(IRankedBattlesController)
    _TOOLTIP_TYPE = TOOLTIP_TYPE.RANKED_SELECTOR_INFO
    _TOOLTIP_WIDTH = _TOOLTIP_MIN_WIDTH

    @staticmethod
    def _getTitle():
        return backport.text(R.strings.ranked_battles.selectorTooltip.title())

    @staticmethod
    def _getDescription():
        return backport.text(R.strings.ranked_battles.selectorTooltip.desc())


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
