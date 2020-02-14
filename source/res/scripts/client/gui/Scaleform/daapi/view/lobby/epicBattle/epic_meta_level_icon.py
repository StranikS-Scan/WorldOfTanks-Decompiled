# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_meta_level_icon.py
import logging
from collections import namedtuple
from helpers import int2roman
_logger = logging.getLogger(__name__)
_BACKGROUND_LEVEL_IMAGE = ((0,),
 (1, 2, 3, 4),
 (5, 6, 7, 8, 9),
 (10, 11, 12, 13, 14),
 (15,))
EpicMetaLevelIconVO = namedtuple('EpicMetaLevelIconVO', ('level', 'cycleNumberHtmlText', 'metLvlBGImageId'))

def getEpicMetaIconVO(seasonLevel, playerLevel):
    playerLevelStr = str(playerLevel) if playerLevel is not None else None
    return EpicMetaLevelIconVO(int2roman(seasonLevel), playerLevelStr, _getEpicMetaIconBackgroundId(playerLevel))


def getEpicMetaIconVODict(seasonLevel, playerLevel):
    return getEpicMetaIconVO(seasonLevel, playerLevel)._asdict()


def _getEpicMetaIconBackgroundId(level):
    if level is None:
        return 0
    else:
        for index, levelRange in enumerate(_BACKGROUND_LEVEL_IMAGE):
            if level in levelRange:
                return index

        return
