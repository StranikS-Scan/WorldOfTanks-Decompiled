# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/tooltips/selectable_reward_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from shared_utils import first

class SelectableCrewbookTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(SelectableCrewbookTooltipData, self).__init__(context, TOOLTIP_TYPE.SELECTABLE_CREWBOOK)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(420)

    def _packBlocks(self, item, **kwargs):
        return [self.__packImageBlock(item.name), self.__packMainBlock(item), self.__packFooterBlock(item.name)]

    @staticmethod
    def __packFooterBlock(itemName):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.tooltips.selectableCrewbook.dyn(itemName).footer())), padding=formatters.packPadding(top=8))], padding=formatters.packPadding(left=-1))

    @staticmethod
    def __packImageBlock(itemName):
        return formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.mapbox.selectableCrewbookTooltip.dyn(itemName)()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-1))

    @classmethod
    def __packMainBlock(cls, item):
        strPath = R.strings.tooltips.selectableCrewbook
        blocks = [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(strPath.dyn(item.name).title())))]
        blocks.append(formatters.packTextBlockData(text=text_styles.gold(backport.text(strPath.allNations()))))
        crewbook, _ = first(item.options.getItems())
        experienceText = text_styles.expText(backport.getIntegralFormat(crewbook.getXP()))
        information = backport.text(strPath.info(), exp=experienceText)
        blocks.append(formatters.packTextBlockData(text=text_styles.main(information)))
        return formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(left=-1), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)
