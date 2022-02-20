# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shop_sales/paid_shuffle_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IShopSalesEventController
BLOCK_WIDTH = 700

class PaidShuffleTooltip(BlocksTooltipData):
    __shopSales = dependency.descriptor(IShopSalesEventController)

    def __init__(self, context):
        super(PaidShuffleTooltip, self).__init__(context, None)
        self._setContentMargin(bottom=10, top=2)
        return

    def _packBlocks(self, *args, **kwargs):
        timeLeft = self.__shopSales.periodicRenewalStartTime - getServerUTCTime()
        if timeLeft < 0:
            timeLeft = timeLeft % self.__shopSales.periodicRenewalPeriod
        rFormat = R.strings.menu.headerButtons.battle.types.ranked.availability
        timeLeftTxt = text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, rFormat))
        return [formatters.packImageTextBlockData(title=text_styles.main(backport.text(R.strings.tooltips.shopSales.paidShuffle.header(), timeout=timeLeftTxt)), img=backport.image(R.images.gui.maps.icons.shopSales.clock()), txtPadding=formatters.packPadding(top=15, left=-10), imgPadding=formatters.packPadding(top=7, left=-12, right=5), blockWidth=BLOCK_WIDTH)]
