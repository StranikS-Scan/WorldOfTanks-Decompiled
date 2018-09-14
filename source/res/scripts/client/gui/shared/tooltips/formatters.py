# Embedded file name: scripts/client/gui/shared/tooltips/formatters.py
from gui.Scaleform.genConsts.BATTLE_RESULT_TYPES import BATTLE_RESULT_TYPES

def packTextBlockDataItem(linkage, data):
    return {'linkage': linkage,
     'data': data}


def packTextBlockData(text, linkage = BATTLE_RESULT_TYPES.TOOLTIP_TEXT_BLOCK_LINKAGE):
    return packTextBlockDataItem(linkage, {'text': text})


def packHeadBlockData(title, icon):
    return packTextBlockDataItem(BATTLE_RESULT_TYPES.TOOLTIP_HEAD_BLOCK_LINKAGE, {'title': title,
     'icon': icon})


def packTotalItemsBlockData(counter, text, counterVisible):
    return packTextBlockDataItem(BATTLE_RESULT_TYPES.TOOLTIP_TOTAL_ITEMS_BLOCK_LINKAGE, {'text': text,
     'counter': counter,
     'counterVisible': counterVisible})


def packTextParameterBlockData(name, value, linkage = BATTLE_RESULT_TYPES.TOOLTIP_TEXT_PARAMETER_LINKAGE):
    return packTextBlockDataItem(linkage, {'name': name,
     'value': value})


def packBuildUpBlockData(blocks, linkage = BATTLE_RESULT_TYPES.TOOLTIP_BUILDUP_BLOCK_LINKAGE):
    return packTextBlockDataItem(linkage, {'blocksData': blocks})


def packResultBlockData(title, text):
    return packBuildUpBlockData([packTextBlockData(title, BATTLE_RESULT_TYPES.TOOLTIP_RESULT_TTILE_LEFT_LINKAGE), packTextBlockData(text, BATTLE_RESULT_TYPES.TOOLTIP_ICON_TEXT_PARAMETER_LINKAGE)])
