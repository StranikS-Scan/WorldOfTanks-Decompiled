# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/after_battle_reward_view_helpers.py
import logging
from collections import namedtuple
from data_structures import OrderedSet
from gui.server_events.bonuses import CreditsBonus, CrystalBonus, GoldBonus, ItemsBonus, GoodiesBonus, BasicPremiumDaysBonus, PlusPremiumDaysBonus, EpicAbilityPtsBonus
from helpers import dependency, int2roman
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
_BACKGROUND_LEVEL_IMAGE = ((0,),
 (1, 2, 3, 4),
 (5, 6, 7, 8, 9),
 (10, 11, 12, 13, 14),
 (15,))
ProgressionLevelIconVO = namedtuple('MetaLevelVO', ('seasonLevel', 'playerLevel', 'bgImageId'))

def formatBonuses(bonuses):

    def __accumulateIntegralBonus(integralBonusType, bonuses):
        return integralBonusType(bonuses[0].getName(), sum([ b.getValue() for b in bonuses ]))

    def accumulateCredits(bonuses):
        return __accumulateIntegralBonus(CreditsBonus, bonuses)

    def accumulateCrystals(bonuses):
        return __accumulateIntegralBonus(CrystalBonus, bonuses)

    def accumulateGold(bonuses):
        return __accumulateIntegralBonus(GoldBonus, bonuses)

    def accumulateBasicPremiumDays(bonuses):
        return __accumulateIntegralBonus(BasicPremiumDaysBonus, bonuses)

    def accumulatePlusPremiumDays(bonuses):
        return __accumulateIntegralBonus(PlusPremiumDaysBonus, bonuses)

    def accumulateEpicAbilityPtsBonus(bonuses):
        return __accumulateIntegralBonus(EpicAbilityPtsBonus, bonuses)

    def accumulateItems(bonuses):
        values = dict()
        for b in bonuses:
            for bid, cnt in b.getValue().iteritems():
                values[bid] = values.get(bid, 0) + cnt

        return ItemsBonus(bonuses[0].getName(), values)

    def accumulateGoodies(bonuses):
        values = dict()
        for b in bonuses:
            for bid, value in b.getValue().iteritems():
                if bid in values.iterkeys():
                    cnt = values.get(bid).get('count', 0)
                    values[bid]['count'] = cnt + value.get('count', 0)
                values[bid] = {'count': value.get('count', 0)}

        return GoodiesBonus(bonuses[0].getName(), values)

    typeToAccumulator = {CreditsBonus: accumulateCredits,
     CrystalBonus: accumulateCrystals,
     GoldBonus: accumulateGold,
     ItemsBonus: accumulateItems,
     GoodiesBonus: accumulateGoodies,
     BasicPremiumDaysBonus: accumulateBasicPremiumDays,
     PlusPremiumDaysBonus: accumulatePlusPremiumDays,
     EpicAbilityPtsBonus: accumulateEpicAbilityPtsBonus}
    bonuses = [ bonus for singleQuestBonuses in bonuses for bonus in singleQuestBonuses ]
    accumulatedBonuses = []
    for bonusType in OrderedSet((type(b) for b in bonuses)):
        bonusesOfType = [ b for b in bonuses if isinstance(b, bonusType) ]
        if bonusType not in typeToAccumulator.iterkeys():
            accumulatedBonuses.extend(bonusesOfType)
        accumulatedBonuses.append(typeToAccumulator.get(bonusType)(bonusesOfType))

    return accumulatedBonuses


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getQuestBonuses(questsProgressData, questIDs, currentLevelQuestID, eventsCache=None):
    allQuests = eventsCache.getAllQuests()
    currentLevelQuest = allQuests.get(currentLevelQuestID, None)
    bonuses = []
    if currentLevelQuest and questsProgressData:
        for questID in questIDs:
            bonuses += [ allQuests.get(q).getBonuses() for q in questsProgressData if questID in q ]

    return bonuses


def getProgressionIconVO(cycleNumber, playerLevel):
    playerLevelStr = str(playerLevel) if playerLevel is not None else None
    return ProgressionLevelIconVO(int2roman(cycleNumber), playerLevelStr, _getProgressionIconBackgroundId(playerLevel))


def getProgressionIconVODict(cycleNumber, playerLevel):
    return getProgressionIconVO(cycleNumber, playerLevel)._asdict()


def _getProgressionIconBackgroundId(level):
    if level is None:
        return 0
    else:
        for index, levelRange in enumerate(_BACKGROUND_LEVEL_IMAGE):
            if level in levelRange:
                return index

        return
