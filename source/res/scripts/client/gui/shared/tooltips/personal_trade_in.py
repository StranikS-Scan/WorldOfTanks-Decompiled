# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/personal_trade_in.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class PersonalTradeInInfoTooltipData(BlocksTooltipData):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, context):
        super(PersonalTradeInInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.PERSONAL_TRADE_IN_INFO)
        self._setWidth(380)
        self._setContentMargin(right=62)

    def _packBlocks(self, *args, **kwargs):
        return [formatters.packBuildUpBlockData(blocks=self.__getHeader(), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_VERTICAL), formatters.packBuildUpBlockData(blocks=self.__getInfo(), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)]

    @staticmethod
    def __getHeader():
        return [formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.tradeIn.trade_in_icon()), title=text_styles.highTitle(backport.text(R.strings.tooltips.personalTradeInInfo.header())), imgPadding=formatters.packPadding(left=2, top=4), txtPadding=formatters.packPadding(left=14, top=12))]

    @staticmethod
    def __getInfo():
        return [formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.prem_small_icon()), imgPadding=formatters.packPadding(top=4), title=text_styles.main(backport.text(R.strings.tooltips.personalTradeInInfo.info())), txtPadding=formatters.packPadding(left=3), padding=formatters.packPadding(left=62, bottom=18)), formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.discount()), imgPadding=formatters.packPadding(top=-1), title=text_styles.main(backport.text(R.strings.tooltips.personalTradeInInfo.discount())), padding=formatters.packPadding(left=62))]
