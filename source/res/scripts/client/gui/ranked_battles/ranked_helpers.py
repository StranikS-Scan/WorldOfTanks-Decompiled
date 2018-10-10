# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers.py
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from helpers import dependency
from debug_utils import LOG_CURRENT_EXCEPTION
from skeletons.gui.lobby_context import ILobbyContext
from gui.ranked_battles.constants import RANKED_QUEST_ID_PREFIX, RANK_TYPES
__ANIMATION_DATA_FIELDS = ['top',
 'bottom',
 'left',
 'right']

def getRankedDataFromTokenQuestID(questID):
    seasonID, cohort, percent = questID.split('_')[-3:]
    return (int(seasonID), int(cohort), int(percent))


def isRankedQuestID(ID):
    return ID[:len(RANKED_QUEST_ID_PREFIX)] == RANKED_QUEST_ID_PREFIX


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRankedBattlesUrl(lobbyContext=None):
    if lobbyContext is None:
        return
    else:
        try:
            return lobbyContext.getServerSettings().bwRankedBattles.rblbHostUrl
        except AttributeError:
            LOG_CURRENT_EXCEPTION()
            return

        return


def buildRankVO(rank, isEnabled=False, hasTooltip=False, imageSize=RANKEDBATTLES_ALIASES.WIDGET_MEDIUM, shieldStatus=None, showShieldLabel=True, shieldAnimated=False, showLadderPoints=False, ladderPoints=None):
    isMaster = rank.getType() == RANK_TYPES.VEHICLE
    shield = None
    if shieldStatus is not None:
        prevShieldHP, shieldHP, _, shieldState, newShieldState = shieldStatus
        if shieldState != newShieldState or shieldHP > 0:
            shieldSize = getShieldSizeByRankSize(imageSize)
            shield = {'state': shieldState,
             'newState': newShieldState,
             'size': shieldSize,
             'img': RES_ICONS.getRankShieldIcon(shieldSize),
             'plateImg': '',
             'prevLabel': '',
             'label': ''}
            if showShieldLabel:
                shield['prevLabel'] = str(prevShieldHP)
                shield['label'] = str(shieldHP)
                shield['plateImg'] = RES_ICONS.getRankShieldPlateIcon(shieldSize)
            if shieldAnimated:
                shield['animationData'] = {'topImg': RES_ICONS.getRankShieldFrameIcon(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_TOP),
                 'bottomImg': RES_ICONS.getRankShieldFrameIcon(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_BOTTOM),
                 'rightImg': RES_ICONS.getRankShieldFrameIcon(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_RIGHT),
                 'leftImg': RES_ICONS.getRankShieldFrameIcon(shieldSize, RANKEDBATTLES_ALIASES.SHIELD_PART_LEFT)}
    scores = None
    if showLadderPoints and not isMaster:
        scoresLabel = ''
        scoresNewLabel = ''
        imgStr = ''
        pntsFormatter = getLadderPointsFormatterBySize(rankSize=imageSize)
        if ladderPoints is None:
            if not rank.isAcquired() and not rank.isLost():
                scoresLabel = pntsFormatter('+')
                imgStr = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_LADDER_POINT
        else:
            points, newPoints = ladderPoints
            scoresLabel = pntsFormatter(str(points))
            scoresNewLabel = '' if newPoints is None else pntsFormatter(str(newPoints))
            imgStr = getLadderPointsIconBySize(rankSize=imageSize)
        scores = {'img': imgStr,
         'label': scoresLabel,
         'newLabel': scoresNewLabel,
         'tooltip': TOOLTIPS.RANKEDBATTLEVIEW_SCOREPOINT}
    finalImageSrc = rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_FINAL) if rank.getIsMaxAccRank() else ''
    return {'imageSrc': rank.getIcon(imageSize),
     'smallImageSrc': rank.getIcon(RANKEDBATTLES_ALIASES.WIDGET_SMALL),
     'finalImageSrc': finalImageSrc,
     'isEnabled': isEnabled,
     'isMaster': isMaster,
     'rankID': str(rank.getID()),
     'hasTooltip': hasTooltip,
     'shield': shield,
     'scoresData': scores}


def getShieldSizeByRankSize(rankSize):
    return RANKEDBATTLES_ALIASES.WIDGET_HUGE if rankSize in RANKEDBATTLES_ALIASES.SHIELD_HUGE_SIZES else RANKEDBATTLES_ALIASES.WIDGET_MEDIUM


def getLadderPointsIconBySize(rankSize):
    return RES_ICONS.MAPS_ICONS_RANKEDBATTLES_LADDER_POINT_HUGE if rankSize == RANKEDBATTLES_ALIASES.WIDGET_HUGE else RES_ICONS.MAPS_ICONS_RANKEDBATTLES_LADDER_POINT


def getLadderPointsFormatterBySize(rankSize):
    return text_styles.promoTitle if rankSize == RANKEDBATTLES_ALIASES.WIDGET_HUGE else text_styles.stats
