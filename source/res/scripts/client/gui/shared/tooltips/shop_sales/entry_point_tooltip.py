# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/shop_sales/entry_point_tooltip.py
from constants import EventPhase
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.game_control import IShopSalesEventController
_PHASE_NAME = {EventPhase.NOT_STARTED: 'locked',
 EventPhase.IN_PROGRESS: 'active',
 EventPhase.FINISHED: 'ended'}
_TOOLTIP_WIDTH = 300
_TOOLTIP_MARGIN = 0
_TOOLTIP_BORDER = 1
_ONE_SIDE_PADDING = 22
_TWO_SIDE_PADDING = _ONE_SIDE_PADDING * 2
_CONTENT_WIDTH = _TOOLTIP_WIDTH - _TWO_SIDE_PADDING

def _getPhaseName(isEnabled, eventPhase):
    return _PHASE_NAME.get(eventPhase, 'disabled') if isEnabled else 'disabled'


class ShopSalesEntryPointTooltipData(BlocksTooltipData):
    __shopSales = dependency.descriptor(IShopSalesEventController)

    def __init__(self, context):
        super(ShopSalesEntryPointTooltipData, self).__init__(context, TOOLTIP_TYPE.SHOP_SALES_ENTRY_POINT)
        self._setContentMargin(_TOOLTIP_MARGIN, _TOOLTIP_MARGIN, _ONE_SIDE_PADDING - 6, _TOOLTIP_BORDER)
        self._setWidth(_TOOLTIP_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        eventPhase = self.__shopSales.currentEventPhase
        _, phaseEnd = self.__shopSales.currentEventPhaseTimeRange
        timeLeft = phaseEnd - getServerUTCTime()
        if timeLeft < 0:
            timeLeft = 0
        savedCount = self.__shopSales.favoritesCount
        blocks = self.__packMainBlocks(eventPhase, timeLeft)
        footer = self.__packFooterBlock(eventPhase, savedCount)
        if footer is not None:
            blocks.append(footer)
        return blocks

    def __packMainBlocks(self, eventPhase, timeLeft):
        return [formatters.packBuildUpBlockData(self.__packHeaderBlocks(eventPhase, timeLeft) + [self.__packDescriptionBlock(eventPhase)])]

    def __packHeaderBlocks(self, eventPhase, timeLeft):
        headerBackgroundBlock = formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.shopSales.header()), padding=formatters.packPadding(top=_TOOLTIP_BORDER, left=_TOOLTIP_BORDER))
        titleBlock = formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.shopSales.header())), blockWidth=_CONTENT_WIDTH)
        headerContentBlock = formatters.packBuildUpBlockData(blocks=(titleBlock, self.__packSubTitleBlock(eventPhase, timeLeft)), padding=formatters.packPadding(top=-(50 + _ONE_SIDE_PADDING), left=_ONE_SIDE_PADDING))
        return [headerBackgroundBlock, headerContentBlock]

    def __packSubTitleBlock(self, eventPhase, timeLeft):
        if self.__shopSales.isEnabled and eventPhase == EventPhase.FINISHED:
            icon = None
            timeLeftTxt = ''
        else:
            icon = backport.image(R.images.gui.maps.icons.shopSales.clock())
            rFormat = R.strings.menu.headerButtons.battle.types.ranked.availability
            timeLeftTxt = text_styles.stats(backport.getTillTimeStringByRClass(timeLeft, rFormat))
        return self.__packImgTextBlock(img=icon, txt=backport.text(self.__getPhaseStringResource(eventPhase).subheader(), timeout=timeLeftTxt), textStyle=text_styles.main, usePadding=False)

    def __packDescriptionBlock(self, eventPhase):
        return formatters.packTextBlockData(text=text_styles.main(backport.text(self.__getPhaseStringResource(eventPhase).desc())), padding=formatters.packPadding(top=_ONE_SIDE_PADDING, left=_ONE_SIDE_PADDING), blockWidth=_CONTENT_WIDTH)

    def __packFooterBlock(self, eventPhase, savedCount):
        if not self.__shopSales.isEnabled:
            return self.__packImgTextBlock(img=backport.image(R.images.gui.maps.icons.shopSales.warning()), txt=backport.text(self.__getPhaseStringResource(eventPhase).footer()))
        elif eventPhase == EventPhase.FINISHED:
            if savedCount:
                return self.__packImgTextBlock(img=backport.image(R.images.gui.maps.icons.shopSales.bookmark()), txt=backport.text(self.__getPhaseStringResource(eventPhase).footer.saved(), count=savedCount))
            return self.__packImgTextBlock(img=backport.image(R.images.gui.maps.icons.shopSales.bookmark()), txt=backport.text(self.__getPhaseStringResource(eventPhase).footer.purchased()))
        else:
            return None

    def __getPhaseStringResource(self, eventPhase):
        return R.strings.tooltips.shopSales.dyn(_getPhaseName(self.__shopSales.isEnabled, eventPhase))

    @staticmethod
    def __packImgTextBlock(txt, img=None, imgSize=37, imgPadding=-8, txtPadding=-6, textStyle=None, usePadding=True):
        if img is not None:
            imgBlocksList = [formatters.packImageBlockData(img=img, padding=formatters.packPadding(top=imgPadding, left=imgPadding), width=imgSize, height=imgSize)]
        else:
            imgSize = imgPadding = txtPadding = 0
            imgBlocksList = []
        txtBlock = formatters.packTextBlockData(text=(textStyle or text_styles.neutral)(txt), padding=formatters.packPadding(left=txtPadding), blockWidth=_CONTENT_WIDTH - imgSize - imgPadding - txtPadding)
        return formatters.packBuildUpBlockData(blocks=imgBlocksList + [txtBlock], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=_ONE_SIDE_PADDING, bottom=txtPadding + imgPadding + 2) if usePadding else None)
