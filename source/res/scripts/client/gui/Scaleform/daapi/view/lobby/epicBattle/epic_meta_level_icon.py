# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_meta_level_icon.py
from collections import namedtuple
__META_LEVEL_BACKGROUND_REL_BASE_PATH = '../maps/icons/epicBattles/metaLvls/{}/bg{}.png'
__META_LEVEL_FOREGROUND_REL_BASE_PATH = '../maps/icons/epicBattles/metaLvls/{}/top_{}_{}.png'
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

class EPIC_META_LEVEL_ICON_SIZE(object):
    SMALL, BIG = ('256x256', '340x340')


def __getForegroundIndexForMetaLevel(metaLevel):
    indexInDict = next((a for a, e in enumerate(__FOREGROUND_TO_META_LEVEL.values()) if metaLevel in e))
    return __FOREGROUND_TO_META_LEVEL.keys()[indexInDict]


def getEpicMetaIconBackground(prestigeLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    return __META_LEVEL_BACKGROUND_REL_BASE_PATH.format(size, prestigeLevel + 1)


def getEpicMetaIconForeground(prestigeLevel, metaLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    return None if metaLevel < 2 else __META_LEVEL_FOREGROUND_REL_BASE_PATH.format(size, prestigeLevel + 1, __getForegroundIndexForMetaLevel(metaLevel))


def getIconImageData(prestigeLevel, metaLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    bg = getEpicMetaIconBackground(prestigeLevel, size)
    fg = getEpicMetaIconForeground(prestigeLevel, metaLevel, size)
    return (bg, fg)


def getEpicMetaIconVO(prestigeLevel, metaLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    bg, fg = getIconImageData(prestigeLevel, metaLevel, size)
    return EpicMetaLevelIconVO(str(metaLevel), bg, fg)


def getEpicMetaIconVODict(prestigeLevel, metaLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    return getEpicMetaIconVO(prestigeLevel, metaLevel, size)._asdict()
