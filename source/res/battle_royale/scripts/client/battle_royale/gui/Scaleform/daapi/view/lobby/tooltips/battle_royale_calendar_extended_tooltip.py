# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tooltips/battle_royale_calendar_extended_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.periodic.prime_helpers import getPrimeTableBlocks
from skeletons.gui.game_control import IBattleRoyaleController
from gui.shared.tooltips import TOOLTIP_TYPE

class BattleRoyaleCalendarExtendedTooltip(BlocksTooltipData):
    __TOOLTIP_MIN_WIDTH = 180
    __connectionMgr = dependency.descriptor(IConnectionManager)
    _battleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, context):
        super(BattleRoyaleCalendarExtendedTooltip, self).__init__(context, TOOLTIP_TYPE.BATTLE_ROYALE_SELECTOR_CALENDAR_INFO)
        self._setWidth(self.__TOOLTIP_MIN_WIDTH)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)

    def _packBlocks(self, *args):
        items = []
        blocks = []
        if self._battleController.getCurrentCycleInfo()[1]:
            blocks.append(self.__packTimeLeftBlock())
            blocks.append(self.__packTimeTableBlock())
        items.append(formatters.packBuildUpBlockData(blocks, 15))
        return items

    def __packTimeLeftBlock(self):
        endDate = self._battleController.getCurrentSeason().getCycleEndDate()
        return self.__getTillEndBlock(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(endDate)))

    def __packTimeTableBlock(self):
        primeTime = self._battleController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
        currentCycleEnd = self._battleController.getCurrentSeason().getCycleEndDate()
        return formatters.packBuildUpBlockData(getPrimeTableBlocks(primeTime, currentCycleEnd, R.strings.ranked_battles.selectorTooltip), 7, blockWidth=self.__TOOLTIP_MIN_WIDTH)

    def __getTillEndBlock(self, timeLeft):
        res = ''.join([text_styles.main(backport.text(R.strings.ranked_battles.selectorTooltip.tillEnd())), ' ', text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.headerButtons.battle.types.ranked.availability))])
        return formatters.packTextBlockData(text=res, blockWidth=self.__TOOLTIP_MIN_WIDTH)
