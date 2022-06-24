# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/stronghold.py
import logging
import typing
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import getReserveNameVO
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import params_helper, formatters as paramsFormatters
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import int2roman
if typing.TYPE_CHECKING:
    from gui.prb_control.items.stronghold_items import StrongholdData
_logger = logging.getLogger(__name__)

class StrongholdTooltipData(BlocksTooltipData):

    def _getEntity(self):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        return dispatcher.getEntity()

    def _getData(self):
        return self._getEntity().getStrongholdSettings()


class ReserveTooltipData(StrongholdTooltipData):
    BIG_ICON_SUFFIX = 'Big'
    BIG_GLOW_ICON_SUFFIX = 'BigGlow'
    LEVELS_WITHOUT_GLOW = 10

    def __init__(self, context):
        super(ReserveTooltipData, self).__init__(context, TOOLTIP_TYPE.RESERVE)

    def _packBlocks(self, *args):
        tooltipBlocks = super(ReserveTooltipData, self)._packBlocks()
        reserves = self._getData().getReserve()
        isPlayerLegionary = self._getEntity().getPlayerInfo().isLegionary()
        reserveId = args[0]
        reserve = reserves.getReserveById(reserveId)
        reserveName = getReserveNameVO(reserve.getType())
        reserveLevel = reserve.getLevel()
        selected = reserve in reserves.getSelectedReserves()
        reserveCount = reserves.getReserveCount(reserve.getType(), reserve.getLevel())
        if selected:
            reserveCount -= 1
        if reserve.intCD is None:
            _logger.error('%s intCD is None! Check wgsh version on staging.', reserveName)
            return tooltipBlocks
        else:
            item = self.context.buildItem(reserve.intCD)
            tooltipBlocks.append(self.__getHeaderBlock(item, reserveName, reserveLevel, reserveCount, isPlayerLegionary))
            tooltipBlocks.append(formatters.packBuildUpBlockData(self.__getMainParamsBlock(reserveName, item), padding=formatters.packPadding(left=10, right=10, top=-4, bottom=-2), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, gap=-2, blockWidth=450))
            tooltipBlocks.append(formatters.packBuildUpBlockData(self.__getAdditionalParamsBlock(reserve), padding=formatters.packPadding(left=10, right=10, top=-4, bottom=-2), gap=-2))
            if selected:
                status = R.strings.fortifications.reserves.tooltip.selected()
            else:
                status = R.strings.fortifications.reserves.tooltip.readyToSelect()
            tooltipBlocks.append(formatters.packAlignedTextBlockData(text_styles.statInfo(backport.text(status)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, blockWidth=430, padding=formatters.packPadding(left=10, right=10, top=-7, bottom=-7)))
            return tooltipBlocks

    def __getHeaderBlock(self, item, name, level, count, isPlayerLegionary):
        reserveIcon = R.images.gui.maps.icons.reserveTypes.dyn(self.__getReserveIconName(name, level))()
        countStr = text_styles.main(backport.text(R.strings.fortifications.reserves.tooltip.inStorage(), count=text_styles.expText(count))) if not isPlayerLegionary else ''
        return formatters.packImageTextBlockData(title=text_styles.highTitle(item.shortUserName), desc='\n'.join([text_styles.neutral(backport.text(R.strings.fortifications.reserves.tooltip.level(), level=int2roman(level))), countStr]), img=backport.image(reserveIcon), imgPadding=formatters.packPadding(left=5, right=10), imgAtLeft=True, txtAlign='left', linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding=formatters.packPadding(top=6), blockWidth=500)

    def __getMainParamsBlock(self, name, item):
        block = [formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.fortifications.reserves.tooltip.mainApplyEffect())), desc=text_styles.standard(backport.text(R.strings.fortifications.reserves.tooltip.applyDescription.dyn(name)())), descPadding=formatters.packPadding(top=4))]
        params = params_helper.getParameters(item)
        paramsResult = paramsFormatters.getFormattedParamsList(item.descriptor, params)
        for paramName, paramValue in paramsResult:
            block.append(self.__packParameterBlock(backport.text(R.strings.menu.moduleInfo.params.dyn(paramName)()), paramValue, paramsFormatters.measureUnitsForParameter(paramName)))

        return block

    def __getAdditionalParamsBlock(self, reserve):
        block = [formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.fortifications.reserves.tooltip.additionalApplyEffect()))), self.__packParameterBlock(reserve.getDescription(), '+%s%%' % reserve.getBonusPercent(), '')]
        return block

    def __packParameterBlock(self, name, value, measureUnits):
        return formatters.packTextParameterBlockData(name=text_styles.concatStylesWithSpace(text_styles.main(name), text_styles.standard(measureUnits)), value=text_styles.stats(value), valueWidth=110, padding=formatters.packPadding(left=-30, top=1), gap=16)

    def __getReserveIconName(self, name, level):
        return name + (self.BIG_GLOW_ICON_SUFFIX if level > self.LEVELS_WITHOUT_GLOW else self.BIG_ICON_SUFFIX)
