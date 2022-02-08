# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_selectable_reward_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES

class RankedSelectableRewardTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(RankedSelectableRewardTooltip, self).__init__(context, TOOLTIP_TYPE.BATTLE_PASS_POINTS)
        self._setContentMargin(top=20, bottom=20, right=20)
        self._setMargins(10, 15)
        self._setWidth(420)

    def _packBlocks(self, *args, **kwargs):
        self._items = super(RankedSelectableRewardTooltip, self)._packBlocks(*args, **kwargs)
        self._items.append(self.__packImageBlock())
        self._items.append(self.__packRewardNamesBlock())
        self._items.append(self.__packLimitBlock())
        return self._items

    @staticmethod
    def __packImageBlock():
        return formatters.packImageBlockData(img=backport.image(R.images.gui.maps.icons.rankedBattles.deluxe_gift_big()), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)

    @staticmethod
    def __packRewardNamesBlock():
        texts = R.strings.ranked_battles.selectableReward.tooltip.equipmentChoice
        blocks = [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(texts.title()))), formatters.packTextBlockData(text=text_styles.main(backport.text(texts.list())))]
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    @staticmethod
    def __packLimitBlock():
        return formatters.packTextBlockData(text=text_styles.standard(backport.text(R.strings.ranked_battles.selectableReward.tooltip.equipmentChoice.limit())))
