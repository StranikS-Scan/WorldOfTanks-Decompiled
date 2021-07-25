# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/battle_royale_widget_tooltip.py
from helpers import int2roman, time_utils
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from gui.shared.tooltips.ranked.ranked_selector_tooltip import RankedSelectorTooltip
from gui.Scaleform.daapi.view.lobby.battle_royale.tooltips.battle_royale_selector_tooltip import getTillBlock, packPerformanceWarningBlock

class BattleRoyaleWidgetTooltip(RankedSelectorTooltip):
    _battleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, context):
        super(BattleRoyaleWidgetTooltip, self).__init__(context)
        self._setWidth(320)
        self._setContentMargin(top=0, left=0, bottom=0, right=0)

    def _packBlocks(self, *args):
        items = [self.__packMainBlock()]
        if self._battleController.getCurrentCycleInfo()[1]:
            items.append(self._packTimeTableBlock(leftPadding=20))
        currentSeason = self._battleController.getCurrentSeason() or self._battleController.getNextSeason()
        seasonIsStarted = self._battleController.getCurrentSeason()
        if self._battleController.getCurrentCycleInfo()[1]:
            currentCycle = currentSeason.getCycleInfo()
            items.append(getTillBlock(seasonIsStarted, True, time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycle.endDate)), leftPadding=20))
        else:
            nextCycle = currentSeason.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp())
            if nextCycle:
                items.append(getTillBlock(seasonIsStarted, False, time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(nextCycle.startDate)), leftPadding=20))
            else:
                waitNext = backport.text(R.strings.menu.headerButtons.battle.types.battleRoyale.extra.finished())
                items.append(formatters.packTitleDescBlock(title=text_styles.main(waitNext), padding=formatters.packPadding(left=20)))
        items.append(packPerformanceWarningBlock(self._battleController.getPerformanceGroup(), leftPadding=20))
        return items

    def __packMainBlock(self):
        header = backport.text(R.strings.tooltips.battleTypes.battleRoyale.header())
        body = backport.text(R.strings.tooltips.battleTypes.battleRoyale.body2())
        currentSeason = self._battleController.getCurrentSeason()
        if currentSeason:
            cycleNumber = self._battleController.getCurrentOrNextActiveCycleNumber(currentSeason)
            seasonResID = R.strings.battle_royale.season.num(currentSeason.getSeasonID())
            seasonName = backport.text(seasonResID.name()) if seasonResID else None
            scheduleStr = backport.text(R.strings.menu.headerButtons.battle.types.battleRoyale.extra.currentCycle(), season=seasonName, cycle=int2roman(cycleNumber))
            body = '{}\n\n\n{}'.format(scheduleStr, backport.text(R.strings.tooltips.battleTypes.battleRoyale.body2()))
        background = backport.image(R.images.gui.maps.icons.battleRoyale.backgrounds.widget_tooltip_background())
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(header), txtPadding=formatters.packPadding(top=16, left=20), desc=text_styles.main(body), descPadding=formatters.packPadding(top=16, left=20), txtOffset=1, txtGap=-1, img=background)
