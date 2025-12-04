# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/view_helpers.py
import typing
from gui.impl.gen import R
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from gui.prb_control.dispatcher import g_prbLoader
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
if typing.TYPE_CHECKING:
    from typing import TypeVar
    from frameworks.wulf import Array
    from gui.server_events.bonuses import SimpleBonus
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    BonusModelType = TypeVar('BonusModelType', bound=BonusModel)
ARENA_BONUS_TYPE_FROM_QUEUE_TYPE_MAPPING = {QUEUE_TYPE.RANDOMS: ARENA_BONUS_TYPE.REGULAR,
 QUEUE_TYPE.RANKED: ARENA_BONUS_TYPE.RANKED,
 QUEUE_TYPE.MAPBOX: ARENA_BONUS_TYPE.MAPBOX,
 QUEUE_TYPE.EPIC: ARENA_BONUS_TYPE.EPIC_BATTLE,
 QUEUE_TYPE.COMP7: ARENA_BONUS_TYPE.COMP7,
 QUEUE_TYPE.VERSUS_AI: ARENA_BONUS_TYPE.VERSUS_AI}

def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None, packer=None, startIndex=0):
    packer = packer or getDefaultBonusPacker()
    tooltipIndex = 0 if tooltipData is None else len(tooltipData)
    for bonus in (b for b in bonuses if b.isShowInGUI()):
        bonusList = packer.pack(bonus)
        withTooltips = bonusList and tooltipData is not None
        bTooltipList = packer.getToolTip(bonus) if withTooltips else []
        bContentIdList = packer.getContentId(bonus) if withTooltips else []
        for bIndex, bModel in enumerate(bonusList):
            bModel.setIndex(bIndex + startIndex)
            if withTooltips:
                tooltipIndex = _packBonusTooltip(bModel, bIndex, bTooltipList, bContentIdList, tooltipData, tooltipIndex)
            bonusModelsList.addViewModel(bModel)

    return


def _packBonusTooltip(bonusModel, bonusIndex, bonusTooltipList, bonusContentIdList, tooltipData, tooltipIndex):
    if tooltipData is None or not bonusTooltipList and not bonusContentIdList:
        return tooltipIndex
    else:
        tooltipIdx = str(tooltipIndex)
        bonusModel.setTooltipId(tooltipIdx)
        if bonusTooltipList:
            tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
        if bonusContentIdList:
            bonusModel.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
        return tooltipIndex + 1


def getLayoutIDByText(textLayoutID):
    path = textLayoutID.split('.')
    res = R.views
    for src in path:
        res = res.dyn(src)

    return res


def getSupportedArenaBonusTypeFor(queueType, isInUnit, isSortie=True):
    if queueType == QUEUE_TYPE.BATTLE_ROYALE:
        arenaBonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD if isInUnit else ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO
    elif queueType == QUEUE_TYPE.STRONGHOLD_UNITS:
        arenaBonusType = ARENA_BONUS_TYPE.SORTIE_2 if isSortie else ARENA_BONUS_TYPE.FORT_BATTLE_2
    else:
        arenaBonusType = ARENA_BONUS_TYPE_FROM_QUEUE_TYPE_MAPPING.get(queueType, ARENA_BONUS_TYPE.UNKNOWN)
    return arenaBonusType


def convertQueueTypeToArenaType(queueType=None):
    dispatcher = g_prbLoader.getDispatcher()
    isInUnit = False
    isSortie = True
    if dispatcher:
        state = dispatcher.getFunctionalState()
        isInUnit = state.isInUnit(state.entityTypeID)
        if queueType is None:
            queueType = dispatcher.getEntity().getQueueType()
        if queueType == QUEUE_TYPE.STRONGHOLD_UNITS:
            isSortie = dispatcher.getEntity().isSortie()
    return getSupportedArenaBonusTypeFor(queueType, isInUnit, isSortie)
