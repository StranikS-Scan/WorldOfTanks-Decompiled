# Embedded file name: scripts/client/gui/shared/tooltips/formatters.py
from gui.Scaleform.genConsts.BATTLE_RESULT_TYPES import BATTLE_RESULT_TYPES
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
TXT_GAP_FOR_BIG_TITLE = 2
TXT_GAP_FOR_SMALL_TITLE = 3

def packPadding(top = 0, left = 0, bottom = 0, right = 0):
    data = {}
    if top != 0:
        data['top'] = top
    if left != 0:
        data['left'] = left
    if bottom != 0:
        data['bottom'] = bottom
    if right != 0:
        data['right'] = right
    return data


def packBlockDataItem(linkage, data, padding = None):
    data = {'linkage': linkage,
     'data': data}
    if padding is not None:
        data['padding'] = padding
    return data


def packTextBlockData(text, useHtml = True, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, padding = None):
    return packBlockDataItem(linkage, {'text': text,
     'useHtml': useHtml}, padding)


def packHeadBlockData(title, icon):
    return packBlockDataItem(BATTLE_RESULT_TYPES.TOOLTIP_HEAD_BLOCK_LINKAGE, {'title': title,
     'icon': icon})


def packTotalItemsBlockData(counter, text, counterVisible):
    return packBlockDataItem(BATTLE_RESULT_TYPES.TOOLTIP_TOTAL_ITEMS_BLOCK_LINKAGE, {'text': text,
     'counter': counter,
     'counterVisible': counterVisible})


def packTextParameterBlockData(name, value, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_PARAMETER_BLOCK_LINKAGE, valueWidth = -1, gap = 5, padding = None):
    data = {'name': name,
     'value': value}
    if valueWidth != -1:
        data['valueWidth'] = valueWidth
    if gap != -1:
        data['gap'] = gap
    return packBlockDataItem(linkage, data, padding)


def packBuildUpBlockData(blocks, gap = 0, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding = None):
    data = {'blocksData': blocks}
    if gap != 0:
        data['gap'] = gap
    return packBlockDataItem(linkage, data, padding)


def packTitleDescBlock(title, desc = None, gap = TXT_GAP_FOR_BIG_TITLE, useHtml = True, textBlockLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding = None):
    blocks = [packTextBlockData(title, useHtml, textBlockLinkage)]
    if desc is not None:
        blocks.append(packTextBlockData(desc, useHtml, textBlockLinkage))
    return packBuildUpBlockData(blocks, gap, blocksLinkage, padding)


def packTitleDescBlockSmallTitle(title, desc = None, useHtml = True, textBlockLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE, blocksLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE, padding = None):
    return packTitleDescBlock(title, desc, TXT_GAP_FOR_SMALL_TITLE, useHtml, textBlockLinkage, blocksLinkage, padding)


def packResultBlockData(title, text):
    return packBuildUpBlockData([packTextBlockData(title, True, BATTLE_RESULT_TYPES.TOOLTIP_RESULT_TTILE_LEFT_LINKAGE), packTextBlockData(text, True, BATTLE_RESULT_TYPES.TOOLTIP_ICON_TEXT_PARAMETER_LINKAGE)])


def packImageTextBlockData(title = None, desc = None, img = None, imgPadding = None, imgAtLeft = True, txtGap = 0, txtOffset = -1, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGETEXT_BLOCK_LINKAGE, padding = None):
    data = {'imageAtLeft': imgAtLeft}
    if title is not None:
        data['title'] = title
    if desc is not None:
        data['description'] = desc
    if img is not None:
        data['imagePath'] = img
    if imgPadding is not None:
        data['imagePadding'] = imgPadding
    if txtGap != 0:
        data['textsGap'] = txtGap
    if txtOffset != 0:
        data['textsOffset'] = txtOffset
    return packBlockDataItem(linkage, data, padding)


def packImageBlockData(img = None, align = BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_IMAGE_BLOCK_LINKAGE, width = -1, height = -1, padding = None):
    data = {'align': align}
    if img is not None:
        data['imagePath'] = img
    if width != -1:
        data['width'] = width
    if height != -1:
        data['height'] = height
    return packBlockDataItem(linkage, data, padding)


def packSaleTextParameterBlockData(name, saleData, linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_SALE_TEXT_PARAMETER_BLOCK_LINKAGE, padding = None):
    return packBlockDataItem(linkage, {'name': name,
     'saleData': saleData}, padding)
