# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_meta_level_icon.py
from collections import namedtuple
from helpers import int2roman
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
_FOREGROUND_TO_META_LEVEL = {None: [1],
 1: range(2, 6),
 2: range(6, 11),
 3: range(11, 16),
 4: range(16, 21),
 5: range(21, 26),
 6: range(26, 30),
 7: [30]}
_AVAILABLE_LEVELS = sum(_FOREGROUND_TO_META_LEVEL.values(), [])
EpicMetaLevelIconVO = namedtuple('EpicMetaLevelIconVO', ('level', 'prestigeLevelHtmlText', 'metLvlBGImageSrc', 'metLvlTopImageSrc'))

class EPIC_META_LEVEL_ICON_SIZE(object):
    SMALL, BIG = ('256x256', '480x500')


def getEpicMetaIconVO(prestigeLevel, metaLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    bg = _getEpicMetaIconBackground(prestigeLevel, size)
    fg = _getEpicMetaIconForeground(prestigeLevel, metaLevel, size)
    return EpicMetaLevelIconVO(str(metaLevel), int2roman(prestigeLevel + 1), bg, fg)


def getEpicMetaIconVODict(prestigeLevel, metaLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    return getEpicMetaIconVO(prestigeLevel, metaLevel, size)._asdict()


def _getForegroundIndexForMetaLevel(metaLevel):
    indexInDict = next((a for a, e in enumerate(_FOREGROUND_TO_META_LEVEL.values()) if metaLevel in e))
    return _FOREGROUND_TO_META_LEVEL.keys()[indexInDict]


def _getEpicMetaIconBackground(prestigeLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    return RES_ICONS.getPrestigeLevelBg(size, prestigeLevel)


def _getEpicMetaIconForeground(prestigeLevel, metaLevel, size=EPIC_META_LEVEL_ICON_SIZE.SMALL):
    return None if metaLevel < 2 else RES_ICONS.getPrestigeLevelForeground(size, '', _getForegroundIndexForMetaLevel(metaLevel))
