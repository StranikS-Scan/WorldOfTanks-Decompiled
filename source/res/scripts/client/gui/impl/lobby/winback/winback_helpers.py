# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_helpers.py
import logging
from collections import OrderedDict, defaultdict
from copy import deepcopy
from enum import Enum
import typing
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from goodies.goodie_constants import GOODIE_VARIETY
from goodies.goodie_helpers import RESOURCES
from gui.impl.gen.view_models.views.lobby.winback.winback_reward_view_model import RewardName
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.server_events import conditions
from gui.server_events.bonuses import getMergedBonusesFromDicts, mergeBonuses
from helpers import dependency
from shared_utils import first, findFirst
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List
    from gui.server_events.event_items import Quest
    from gui.server_events.bonuses import SimpleBonus, SelectableBonus
_logger = logging.getLogger(__name__)

class SelectableTypes(object):
    VEHICLE = 'vehicle'
    DISCOUNT = 'discount'
    BLUEPRINTS = 'blueprints'


class WinbackQuestTypes(Enum):
    NORMAL = 'normal'
    COMPENSATION = 'compensation'


TOKEN_TO_REWARD_MAPPING = {SelectableTypes.VEHICLE: RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value,
 SelectableTypes.BLUEPRINTS: RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value,
 SelectableTypes.DISCOUNT: RewardName.SELECTABLE_VEHICLE_DISCOUNT.value}

@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache)
def getDiscountFromGoody(goodyID, goodiesCache=None):
    discount = 0
    currency = None
    goodyData = goodiesCache.getGoodieByID(goodyID)
    if goodyData.variety == GOODIE_VARIETY.DISCOUNT:
        resource = goodyData.resource
        denominator = 1 if resource.isPercentage else 100
        discount = resource.value / denominator
        currency = RESOURCES.get(resource.resourceType)
        if currency is None:
            _logger.error('Not supported discount type')
    return (discount, currency)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def getDiscountFromBlueprint(blueprintCD, count=1, itemsCache=None, lobbyContext=None):
    discount = 0
    blueprintsConfig = lobbyContext.getServerSettings().blueprintsConfig
    if getFragmentType(blueprintCD) == BlueprintTypes.VEHICLE:
        vehicle = itemsCache.items.getItemByCD(blueprintCD)
        if count >= blueprintsConfig.getFragmentCount(vehicle.level):
            return 100
        discount = blueprintsConfig.getFragmentDiscount(vehicle.level) * count * 100
    return discount


def getLevelFromSelectableToken(tokenID):
    return tokenID.replace('_gift', '').rsplit(':', 1)[-1]


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getWinbackCompletedQuestsCount(eventsCache=None):
    countCompletedQuests = 0
    epicQuest = eventsCache.getDailyEpicQuest()
    epicDailyToken = first((t for t in epicQuest.accountReqs.getTokens() if t.isDailyQuest()))
    if epicDailyToken is not None:
        countCompletedQuests = eventsCache.questsProgress.getTokenCount(epicDailyToken.getID())
    return countCompletedQuests


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getNonCompensationToken(tokenId, itemsCache=None):
    vehicleToken = tokenId.replace(SelectableTypes.BLUEPRINTS, SelectableTypes.VEHICLE)
    discountToken = tokenId.replace(SelectableTypes.BLUEPRINTS, SelectableTypes.DISCOUNT)
    if itemsCache.items.tokens.getTokenCount(vehicleToken):
        return vehicleToken
    else:
        return discountToken if itemsCache.items.tokens.getTokenCount(discountToken) else None


def getWinbackQuestsData(sortedQuests, dailyQuestTokensCount):
    from gui.impl.lobby.winback.winback_bonus_packer import getWinbackBonuses, cutWinbackTokens
    from gui.selectable_reward.common import WinbackSelectableRewardManager
    questsData = OrderedDict()
    for questNumber, quest in sortedQuests.iteritems():
        bonusesData = None
        received = True if dailyQuestTokensCount >= questNumber else False
        questsData[questNumber] = {}
        selectableBonus = findFirst(lambda b: b.getName() == SELECTABLE_BONUS_NAME, quest.getBonuses())
        if selectableBonus is not None:
            offer = WinbackSelectableRewardManager.getBonusOffer(selectableBonus)
            questsData[questNumber]['offer'] = offer
            if dailyQuestTokensCount >= questNumber and offer is not None and not offer.isOfferAvailable:
                bonusesData = first(WinbackSelectableRewardManager.getBonusReceivedOptions(selectableBonus, WinbackSelectableRewardManager.giftRawBonusesExtractor))
                rawQuestBonusesData = quest.getData().get('bonus', {})
                questBonusesData = deepcopy(rawQuestBonusesData)
                questBonusesData, _ = cutWinbackTokens(questBonusesData)
                if bonusesData and questBonusesData:
                    bonusesData = getMergedBonusesFromDicts([bonusesData, questBonusesData])
        if bonusesData is None:
            bonusesData = quest.getData().get('bonus', {})
        questsData[questNumber]['bonuses'] = getWinbackBonuses(bonusesData, received=received)

    return questsData


@dependency.replace_none_kwargs(winbackController=IWinbackController)
def getSortedWinbackQuests(winBackQuests, dailyQuestTokensCount, winbackController=None):
    questsPairs = defaultdict(lambda : {WinbackQuestTypes.NORMAL: [],
     WinbackQuestTypes.COMPENSATION: []})
    for quest in winBackQuests.values():
        questNumber = winbackController.getQuestIdx(quest)
        if questNumber > 0:
            questType = winbackController.getQuestType(quest.getID())
            questsPairs[questNumber][questType].append(quest)

    quests = filterWinbackQuests(questsPairs, dailyQuestTokensCount)
    return OrderedDict(sorted(quests, key=lambda item: item[0]))


def getLastWinbackQuestData(sortedQuests, winBackData):
    lastQuestData = {}
    if not sortedQuests:
        return {}
    lastQuestNumber = max(sortedQuests)
    lastQuest = sortedQuests[lastQuestNumber]
    bonuses = winBackData.get('quests', {}).get(lastQuestNumber, {}).get('bonuses', [])
    if bonuses:
        extendLastQuestBonuses(bonuses)
    lastQuestData['bonuses'] = bonuses
    winBackData['quests'][lastQuestNumber]['bonuses'] = []
    lastQuestDailyToken = first((t for t in lastQuest.accountReqs.getTokens() if t.isDailyQuest()))
    lastQuestData['token'] = lastQuestDailyToken
    return lastQuestData


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def extendLastQuestBonuses(winBackBonuses, eventsCache=None):
    epicQuest = eventsCache.getDailyEpicQuest()
    winBackBonuses.extend(epicQuest.getBonuses())
    mergeBonuses(winBackBonuses)
    return winBackBonuses


def filterWinbackQuests(questsPairs, countCompletedQuests):
    result = []
    for questNumber, questPair in questsPairs.items():
        normal = first(questPair.get(WinbackQuestTypes.NORMAL))
        compensation = first(questPair.get(WinbackQuestTypes.COMPENSATION))
        if compensation is not None and compensation.getProgressData():
            result.append((questNumber, compensation))
        if normal is not None:
            if questNumber > countCompletedQuests:
                for cond in normal.accountReqs.getConditions().items:
                    if isinstance(cond, conditions.VehiclesUnlocked):
                        if not cond.isAvailable():
                            result.append((questNumber, compensation))
                            break
                else:
                    result.append((questNumber, normal))

            else:
                result.append((questNumber, normal))

    return result
