# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/dragon_boat.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData

class DragonBoatPointsTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(DragonBoatPointsTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.DRAGON_BOAT_POINTS_INFO)
        self._setWidth(360)

    def _packBlocks(self, *args, **kwargs):
        self._items = super(DragonBoatPointsTooltipData, self)._packBlocks(*args, **kwargs)
        titleBlock = formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.tooltips.awardItem.dragonBoatPoints.header())))
        imageBlock = formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.quests.bonuses.big.dragonBoatPoints()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
        titleImageBlock = formatters.packBuildUpBlockData([titleBlock, imageBlock])
        self._items.append(titleImageBlock)
        descriptionBlock = text_styles.main(backport.text(R.strings.tooltips.awardItem.dragonBoatPoints.body()))
        self._items.append(formatters.packTextBlockData(descriptionBlock))
        return self._items
