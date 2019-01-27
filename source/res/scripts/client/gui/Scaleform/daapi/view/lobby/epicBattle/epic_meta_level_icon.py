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

def getEpicMetaIconVO(prestigeLevel, metaLevel):
    bg = _getEpicMetaIconBackground(prestigeLevel)
    fg = _getEpicMetaIconForeground(metaLevel)
    prestigeStr = int2roman(prestigeLevel) if prestigeLevel else ''
    return EpicMetaLevelIconVO(str(metaLevel), prestigeStr, bg, fg)


def getEpicMetaIconVODict(prestigeLevel, metaLevel):
    return getEpicMetaIconVO(prestigeLevel, metaLevel)._asdict()


def _getForegroundIndexForMetaLevel(metaLevel):
    indexInDict = next((a for a, e in enumerate(_FOREGROUND_TO_META_LEVEL.values()) if metaLevel in e))
    return _FOREGROUND_TO_META_LEVEL.keys()[indexInDict]


def _getEpicMetaIconBackground(prestigeLevel):
    return RES_ICONS.getPrestigeLevelBg(prestigeLevel)


def _getEpicMetaIconForeground(metaLevel):
    return None if metaLevel < 2 else RES_ICONS.getPrestigeLevelForeground(_getForegroundIndexForMetaLevel(metaLevel))
