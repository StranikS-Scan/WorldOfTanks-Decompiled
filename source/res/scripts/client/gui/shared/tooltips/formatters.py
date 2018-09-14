# Embedded file name: scripts/client/gui/shared/tooltips/formatters.py
from gui.Scaleform.genConsts.BATTLE_RESULT_TYPES import BATTLE_RESULT_TYPES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
TXT_GAP_FOR_BIG_TITLE = 2
TXT_GAP_FOR_SMALL_TITLE = 3

def packBlockDataItem(linkage, data):
    return {'linkage': linkage,
     'data': data}


def packTextBlockData(text, useHtml = True, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE):
    return packBlockDataItem(linkage, {'text': text,
     'useHtml': useHtml})


def packHeadBlockData(title, icon):
    return packBlockDataItem(BATTLE_RESULT_TYPES.TOOLTIP_HEAD_BLOCK_LINKAGE, {'title': title,
     'icon': icon})


def packTotalItemsBlockData(counter, text, counterVisible):
    return packBlockDataItem(BATTLE_RESULT_TYPES.TOOLTIP_TOTAL_ITEMS_BLOCK_LINKAGE, {'text': text,
     'counter': counter,
     'counterVisible': counterVisible})


def packTextParameterBlockData(name, value, linkage = BATTLE_RESULT_TYPES.TOOLTIP_TEXT_PARAMETER_LINKAGE):
    return packBlockDataItem(linkage, {'name': name,
     'value': value})


def packBuildUpBlockData(blocks, gap = 0, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE):
    return packBlockDataItem(linkage, {'blocksData': blocks,
     'gap': gap})


def packTitleDescBlock(title, desc = None, gap = TXT_GAP_FOR_BIG_TITLE, useHtml = True, textBlockLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE):
    blocks = [packTextBlockData(title, useHtml, textBlockLinkage)]
    if desc is not None:
        blocks.append(packTextBlockData(desc, useHtml, textBlockLinkage))
    return packBuildUpBlockData(blocks, gap, blocksLinkage)


def packTitleDescBlockSmallTitle(title, desc = None, useHtml = True, textBlockLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE):
    return packTitleDescBlock(title, desc, TXT_GAP_FOR_SMALL_TITLE, useHtml, textBlockLinkage, blocksLinkage)


def packResultBlockData(title, text):
    return packBuildUpBlockData([packTextBlockData(title, True, BATTLE_RESULT_TYPES.TOOLTIP_RESULT_TTILE_LEFT_LINKAGE), packTextBlockData(text, True, BATTLE_RESULT_TYPES.TOOLTIP_ICON_TEXT_PARAMETER_LINKAGE)])


def packImageTextBlockData(title = None, desc = None, img = None, imgPadding = None, imgAtLeft = True, txtGap = 0, txtOffset = -1, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE):
    return packBlockDataItem(linkage, {'title': title,
     'description': desc,
     'imagePath': img,
     'imagePadding': imgPadding,
     'imageAtLeft': imgAtLeft,
     'textsGap': txtGap,
     'textsOffset': txtOffset})
