# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/rts/rts_selector_tooltip.py
from gui.impl.gen import R
from gui.impl import backport
from gui.periodic_battles.models import PeriodType
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.periodic.prime_helpers import getPrimeTableBlocks
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRTSBattlesController
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
_CONTENT_MARGINS = {'top': 18,
 'bottom': 18,
 'left': 20,
 'right': 20}
_TOOLTIP_MIN_WIDTH = 320

def _deltaFormatter(delta):
    return text_styles.stats(backport.getTillTimeStringByRClass(delta, R.strings.rts_battles.selectorTooltip.timeLeft))


class RtsSelectorTooltip(BlocksTooltipData):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, ctx):
        super(RtsSelectorTooltip, self).__init__(ctx, TOOLTIP_TYPE.RTS_SELECTOR_INFO)
        self._setContentMargin(**_CONTENT_MARGINS)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(RtsSelectorTooltip, self)._packBlocks()
        periodInfo = self.__rtsController.getPeriodInfo()
        items.append(self.__getHeader(periodInfo))
        items.append(self.__getDescription())
        if self.__rtsController.isAvailable() and self.__rtsController.isBattlesPossible():
            primeTime = self.__rtsController.getPrimeTimes().get(self.__connectionMgr.peripheryID)
            currentCycleEnd = self.__rtsController.getCurrentSeason().getCycleEndDate()
            items.append(formatters.packBuildUpBlockData(getPrimeTableBlocks(primeTime, currentCycleEnd, R.strings.rts_battles.selectorTooltip), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        return items

    @classmethod
    def __getHeader(cls, periodInfo):
        resShortcut = R.strings.rts_battles.selectorTooltip.header
        params = periodInfo.getVO(deltaFmt=_deltaFormatter, withBDeltas=True)
        desc = backport.text(resShortcut.body.dyn(periodInfo.periodType.value, resShortcut.body.default)(), **params)
        return formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.battleTypes.c_64x64.rts()), title=text_styles.middleTitle(backport.text(resShortcut.title())), desc=text_styles.error(desc) if periodInfo.periodType == PeriodType.FROZEN else text_styles.main(desc), txtPadding=formatters.packPadding(top=9), padding=formatters.packPadding(top=-5))

    @staticmethod
    def __getDescription():
        return formatters.packTextBlockData(text_styles.main(backport.text(R.strings.rts_battles.selectorTooltip.description.text())))
