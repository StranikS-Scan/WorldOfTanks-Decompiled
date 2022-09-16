# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_selector.py
import typing
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.periodic.prime_helpers import getPrimeTableBlocks
from helpers import dependency, time_utils
from skeletons.connection_mgr import IConnectionManager
if typing.TYPE_CHECKING:
    from skeletons.gui.game_control import ISeasonProvider

class SeasonalBattleSelectorTooltip(BlocksTooltipData):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    _battleController = None
    _TOOLTIP_TYPE = None
    _TOOLTIP_WIDTH = None
    _R_BATTLE_SELECTOR_STR = R.strings.tooltips.seasonalBattleSelector

    def __init__(self, ctx):
        super(SeasonalBattleSelectorTooltip, self).__init__(ctx, self._TOOLTIP_TYPE)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=20)
        self._setWidth(self._TOOLTIP_WIDTH)

    def _packBlocks(self, *_, **__):
        items = super(SeasonalBattleSelectorTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        items.append(self._packTimeTableBlock())
        items.append(self._packTillEndBlock())
        return items

    @classmethod
    def _packHeaderBlock(cls):
        return formatters.packTitleDescBlock(title=text_styles.highTitle(cls._getTitle()), desc=text_styles.main(cls._getDescription()))

    @classmethod
    def _packTimeTableBlock(cls, leftPadding=0, bottomPadding=0):
        primeTime = cls._battleController.getPrimeTimes().get(cls.__connectionMgr.peripheryID)
        currentCycleEnd = cls._battleController.getCurrentSeason().getCycleEndDate()
        return formatters.packBuildUpBlockData(getPrimeTableBlocks(primeTime, currentCycleEnd, R.strings.ranked_battles.selectorTooltip), 7, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=leftPadding, bottom=bottomPadding))

    @classmethod
    def _packTillEndBlock(cls):
        endTime = time_utils.makeLocalServerTime(cls._battleController.getCurrentSeason().getCycleEndDate())
        timeLeft = time_utils.getTimeDeltaFromNow(endTime)
        return formatters.packTextBlockData(text_styles.main(backport.text(cls._R_BATTLE_SELECTOR_STR.tillEnd())) + ' ' + text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, R.strings.tooltips.tillTime)))

    @classmethod
    def _packTimeTableHeaderBlock(cls):
        return formatters.packImageTextBlockData(title=text_styles.stats(backport.text(cls._R_BATTLE_SELECTOR_STR.timeTable.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=2), txtPadding=formatters.packPadding(left=5))

    @staticmethod
    def _packTimeBlock(message, timeStr):
        return formatters.packTextParameterBlockData(value=timeStr, name=message, valueWidth=97)

    @classmethod
    def _packPeriods(cls, periods):
        if periods:
            periodsStr = []
            for periodStart, periodEnd in periods:
                startTime = formatDate('%H:%M', periodStart)
                endTime = formatDate('%H:%M', periodEnd)
                periodsStr.append(backport.text(cls._R_BATTLE_SELECTOR_STR.timeTable.interval(), start=startTime, end=endTime))

            return '\n'.join(periodsStr)
        return backport.text(cls._R_BATTLE_SELECTOR_STR.timeTable.empty())

    @staticmethod
    def _getTitle():
        raise NotImplementedError

    @staticmethod
    def _getDescription():
        raise NotImplementedError
