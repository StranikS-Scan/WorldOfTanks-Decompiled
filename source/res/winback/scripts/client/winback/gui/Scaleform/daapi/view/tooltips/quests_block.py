# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/Scaleform/daapi/view/tooltips/quests_block.py
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles, icons
from gui.server_events.awards_formatters import AWARDS_SIZES, getEpicViewAwardPacker
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES

def getQuestTooltipBlock(quest):
    return formatters.packBuildUpBlockData([_packQuestInfo(quest), _packQuestRewards(quest)])


def _packQuestInfo(quest):
    title = text_styles.middleTitle(quest.getUserName())
    if quest.isCompleted():
        name = text_styles.concatStylesToSingleLine(icons.check(), title)
        selfPadding = formatters.packPadding(top=-3, left=14, right=20)
        descPadding = formatters.packPadding(left=6, top=-6)
    else:
        name = title
        selfPadding = formatters.packPadding(left=20, right=20)
        descPadding = formatters.packPadding(top=-2)
    return formatters.packTitleDescBlock(title=name, desc=text_styles.main(quest.getDescription()), padding=selfPadding, descPadding=descPadding)


def _packQuestRewards(quest):
    packer = getEpicViewAwardPacker()
    return formatters.packBuildUpBlockData([ _packQuestReward(bonus) for bonus in packer.format(quest.getBonuses()) ], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(left=20, right=20), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)


def _packQuestReward(bonus):
    if bonus.label.startswith('x'):
        align = BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT
        padding = formatters.packPadding(top=-14, right=12)
    else:
        align = BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER
        padding = formatters.packPadding(top=-14)
    iconBlock = formatters.packQuestRewardItemBlockData(img=bonus.getImage(AWARDS_SIZES.SMALL), overlayPath=bonus.getOverlayIcon(AWARDS_SIZES.SMALL), overlayPadding=formatters.packPadding(left=-24, top=-24), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
    textBlock = formatters.packAlignedTextBlockData(text=bonus.getFormattedLabel(), align=align, padding=padding)
    return formatters.packBuildUpBlockData(blocks=[iconBlock, textBlock], blockWidth=72, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-8, bottom=-6))
