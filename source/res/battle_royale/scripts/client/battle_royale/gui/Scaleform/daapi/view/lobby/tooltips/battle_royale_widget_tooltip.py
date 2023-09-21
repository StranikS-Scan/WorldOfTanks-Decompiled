# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tooltips/battle_royale_widget_tooltip.py
from helpers import time_utils
from gui.impl.gen import R
from gui.impl import backport
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
from gui.shared.tooltips.ranked.ranked_selector_tooltip import RankedSelectorTooltip
from battle_royale.gui.Scaleform.daapi.view.lobby.tooltips.battle_royale_selector_tooltip import packPerformanceWarningBlock
from gui.shared.tooltips.periodic.prime_helpers import getPrimeTableWidgetBlocks
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from skeletons.connection_mgr import IConnectionManager

class BattleRoyaleWidgetTooltip(RankedSelectorTooltip):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    _battleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, context):
        super(BattleRoyaleWidgetTooltip, self).__init__(context)
        self._setWidth(320)
        self._setContentMargin(top=0, left=0, bottom=10, right=0)

    def _packBlocks(self, *args):
        items = [formatters.packBuildUpBlockData([self.__packMainBlock()], padding=formatters.packPadding(right=20, bottom=-15))]
        if self._battleController.getCurrentCycleInfo()[1]:
            items.append(formatters.packBuildUpBlockData(self.__packTimeTableWidgetBlock(), 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=20, bottom=-15)))
        items.append(formatters.packBuildUpBlockData([self.__packTimeLeftSeasonBlock()], padding=formatters.packPadding(left=20, bottom=-15, top=-5)))
        items.append(packPerformanceWarningBlock(self._battleController.getPerformanceGroup(), leftPadding=20, rightPadding=10))
        return items

    def __packMainBlock(self):
        header = backport.text(R.strings.tooltips.battleTypes.battleRoyale.header())
        body = backport.text(R.strings.tooltips.battleTypes.battleRoyale.widget.body2())
        currentCycleInfo = self._battleController.getCurrentCycleInfo()
        if currentCycleInfo[1]:
            timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleInfo[0]))
            scheduleStr = ' '.join((backport.text(R.strings.tooltips.battleTypes.battleRoyale.tillEnd()), backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.ranked.availability)))
            body = '{}\n\n\n{}'.format(scheduleStr, backport.text(R.strings.tooltips.battleTypes.battleRoyale.widget.body2()))
        background = backport.image(R.images.gui.maps.icons.battleRoyale.backgrounds.widget_tooltip_background())
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(header), txtPadding=formatters.packPadding(top=16, left=20), desc=text_styles.main(body), descPadding=formatters.packPadding(top=16, left=20), txtOffset=1, txtGap=-1, img=background)

    def __packTimeTableWidgetBlock(self):
        primeTime = self._battleController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
        currentCycleEnd = self._battleController.getCurrentSeason().getCycleEndDate()
        return getPrimeTableWidgetBlocks(primeTime, currentCycleEnd, R.strings.tooltips.battleTypes.battleRoyale.widget, tableTopPadding=-4, ignoreHeaderImageSize=True)

    def __packTimeLeftSeasonBlock(self):
        timeLeft = 10000
        description = ' '.join((text_styles.main(backport.text(R.strings.tooltips.battleTypes.battleRoyale.widget.tillEnd())), text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.ranked.availability))))
        return formatters.packTextBlockData(text=description)
