# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_helpers.py
import logging
from enum import Enum
import typing
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from goodies.goodie_constants import GOODIE_VARIETY
from goodies.goodie_helpers import RESOURCES
from gui.impl.gen.view_models.views.lobby.winback.winback_reward_view_model import RewardName
from helpers import dependency
from shared_utils import first
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
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
