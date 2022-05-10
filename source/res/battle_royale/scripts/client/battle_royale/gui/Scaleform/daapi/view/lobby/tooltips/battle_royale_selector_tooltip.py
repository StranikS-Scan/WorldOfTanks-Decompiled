# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tooltips/battle_royale_selector_tooltip.py
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.tooltips import formatters
from helpers import dependency, time_utils
from gui.shared.tooltips.ranked.ranked_selector_tooltip import RankedSelectorTooltip
from skeletons.gui.game_control import IBattleRoyaleController
from battle_royale.gui.constants import BattleRoyalePerfProblems
from gui.shared.formatters import text_styles, icons

def getTillBlock(isSeasonStarted, tillEnd, timeLeft, leftPadding=0):
    if isSeasonStarted:
        tillStartStr = R.strings.tooltips.battleTypes.battleRoyale.tillStart
        tillEndStr = R.strings.tooltips.battleTypes.battleRoyale.tillEnd
    else:
        tillStartStr = R.strings.tooltips.battleTypes.battleRoyale.tillStartCycle
        tillEndStr = R.strings.tooltips.battleTypes.battleRoyale.tillEndCycle
    return formatters.packTextBlockData(text_styles.main(backport.text(tillEndStr() if tillEnd else tillStartStr())) + ' ' + text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.ranked.availability)), padding=formatters.packPadding(left=leftPadding))


def packPerformanceWarningBlock(performanceGroup, leftPadding=0, rightPadding=0):
    attention = R.strings.epic_battle.selectorTooltip.epicBattle.attention
    if performanceGroup == BattleRoyalePerfProblems.HIGH_RISK:
        icon = icons.markerBlocked()
        titleStyle = text_styles.error
        attention = attention.assuredLowPerformance
    elif performanceGroup == BattleRoyalePerfProblems.MEDIUM_RISK:
        icon = icons.alert()
        titleStyle = text_styles.alert
        attention = attention.possibleLowPerformance
    else:
        icon = icons.attention()
        titleStyle = text_styles.stats
        attention = attention.informativeLowPerformance
    return formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icon, titleStyle(backport.text(attention.title()))), desc=text_styles.main(backport.text(attention.description())), padding=formatters.packPadding(left=leftPadding, right=rightPadding))


class BattleRoyaleSelectorTooltip(RankedSelectorTooltip):
    _battleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, context):
        super(BattleRoyaleSelectorTooltip, self).__init__(context)
        self._setWidth(320)

    def _packBlocks(self, *args):
        items = []
        if self._battleController.isFrozen() or not self._battleController.isEnabled():
            items.append(self.__packFrozenBlock())
        else:
            items.append(self.__packMainBlock())
            currentSeason = self._battleController.getCurrentSeason() or self._battleController.getNextSeason()
            seasonIsStarted = self._battleController.getCurrentSeason()
            if self._battleController.getCurrentCycleInfo()[1]:
                items.append(self._packTimeTableBlock())
                currentCycle = currentSeason.getCycleInfo()
                items.append(getTillBlock(seasonIsStarted, True, time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycle.endDate))))
            elif currentSeason is not None:
                nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
                if nextCycle:
                    items.append(getTillBlock(seasonIsStarted, False, time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(nextCycle.startDate))))
                else:
                    wait = backport.text(R.strings.menu.headerButtons.battle.types.battleRoyale.extra.finished())
                    items.append(formatters.packTitleDescBlock(title=text_styles.main(wait)))
            items.append(packPerformanceWarningBlock(self._battleController.getPerformanceGroup()))
        return items

    def __packMainBlock(self):
        header = backport.text(R.strings.tooltips.battleTypes.battleRoyale.header())
        body = '{}\n\n{}'.format(backport.text(R.strings.tooltips.battleTypes.battleRoyale.body()), backport.text(R.strings.tooltips.battleTypes.battleRoyale.body2()))
        return formatters.packTitleDescBlock(title=text_styles.middleTitle(header), desc=text_styles.main(body))

    def __packFrozenBlock(self):
        return formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.battleTypes.battleRoyale.frozen.body())))
