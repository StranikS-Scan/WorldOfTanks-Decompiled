# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_meta_level_icon.py
from collections import namedtuple
__META_LEVEL_BACKGROUND_REL_BASE_PATH = '../maps/icons/epicBattles/metaLvls/256x256/bg{}.png'
__META_LEVEL_FOREGROUND_REL_BASE_PATH = '../maps/icons/epicBattles/metaLvls/256x256/top_{}_{}.png'
__FOREGROUND_TO_META_LEVEL = {None: [1],
 2: range(2, 6),
 3: range(6, 11),
 4: range(11, 16),
 5: range(16, 21),
 6: range(21, 26),
 7: range(26, 30),
 8: [30]}
_AVAILABLE_LEVELS = sum(__FOREGROUND_TO_META_LEVEL.values(), [])
EpicMetaLevelIconVO = namedtuple('EpicMetaLevelIconVO', ('level', 'metLvlBGImageSrc', 'metLvlTopImageSrc'))

def __getForegroundIndexForMetaLevel(metaLevel):
    indexInDict = next((a for a, e in enumerate(__FOREGROUND_TO_META_LEVEL.values()) if metaLevel in e))
    return __FOREGROUND_TO_META_LEVEL.keys()[indexInDict]


def getEpicMetaIconBackground(prestigeLevel):
    return __META_LEVEL_BACKGROUND_REL_BASE_PATH.format(prestigeLevel + 1)


def getEpicMetaIconForeground(prestigeLevel, metaLevel):
    return None if metaLevel < 2 else __META_LEVEL_FOREGROUND_REL_BASE_PATH.format(prestigeLevel + 1, __getForegroundIndexForMetaLevel(metaLevel))


def getIconImageData(prestigeLevel, metaLevel):
    bg = getEpicMetaIconBackground(prestigeLevel)
    fg = getEpicMetaIconForeground(prestigeLevel, metaLevel)
    return (bg, fg)


def getEpicMetaIconVO(prestigeLevel, metaLevel):
    bg, fg = getIconImageData(prestigeLevel, metaLevel)
    return EpicMetaLevelIconVO(str(metaLevel), bg, fg)


def getEpicMetaIconVODict(prestigeLevel, metaLevel):
    return getEpicMetaIconVO(prestigeLevel, metaLevel)._asdict()
