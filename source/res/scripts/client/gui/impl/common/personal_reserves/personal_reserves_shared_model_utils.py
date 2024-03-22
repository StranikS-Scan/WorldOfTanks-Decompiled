# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/personal_reserves/personal_reserves_shared_model_utils.py
from collections import namedtuple, defaultdict
from time import time
import typing
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE, BoosterCategory
from gui.goodies.goodie_items import Booster, getFullNameForBoosterIcon, BoosterUICommon, BoostersType, getBoosterGuiType
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import BOOST_CATEGORY_TO_RESERVE_TYPE_LOOKUP, BOOSTER_STATE_TO_BOOSTER_MODEL_STATE, PREMIUM_BOOSTER_IDS, EVENT_BOOSTER_IDS, PERSONAL_RESOURCE_ORDER
from gui.impl.gen.view_models.common.personal_reserves.booster_model import BoosterModel, ReserveKind
from gui.impl.gen.view_models.common.personal_reserves.reserves_group_model import GroupCategory, ReservesGroupModel
from gui.impl.lobby.personal_reserves.personal_reserves_utils import getGUIResourceOrder, getNearestExpiryTimeAndAmountByGroup, getTotalBoostersByResourceType, getNearestExpirationTimeAndCountForToday, getTotalLimitedBoostersByResourceType
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.time_utils import ONE_DAY, ONE_YEAR, makeLocalServerTime
if typing.TYPE_CHECKING:
    from typing import Dict, List, Iterable, Optional, Union
    from skeletons.gui.game_control import IBoostersController
    from skeletons.gui.goodies import IBoostersStateProvider, IGoodiesCache
    from frameworks.wulf import Array

class BoosterModelData(namedtuple('BoosterModelArgs', ['resourceType',
 'category',
 'booster',
 'depotCount',
 'forcePremium',
 'showHint'])):

    def __new__(cls, resourceType, category, booster=None, depotCount=0, forcePremium=False, showHint=False):
        return cls._make((resourceType,
         category,
         booster,
         depotCount,
         forcePremium,
         showHint))

    def validate(self, data):
        allowedFields = self._fields
        validData = {k:v for k, v in data.iteritems() if k in allowedFields}
        return validData

    def replace(self, **kwargs):
        return self._replace(**self.validate(kwargs))


RESERVE_GROUP_CATEGORY_LOOKUP = {GOODIE_RESOURCE_TYPE.XP: GroupCategory.XP,
 GOODIE_RESOURCE_TYPE.CREDITS: GroupCategory.CREDITS,
 GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP: GroupCategory.COMBINED_XP,
 GOODIE_RESOURCE_TYPE.FL_XP: GroupCategory.EVENT}
NO_FUTURE_GIVEN = time() + ONE_YEAR * 10

def getPersonalBoosterModelDataByResourceType(cache, controller=None):
    groupedBoosterModelDataByResourceType = defaultdict(list)
    category = BoosterCategory.PERSONAL
    enabledBoosters = cache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ENABLED)
    sortedBoostersList = sorted(enabledBoosters.values(), key=lambda booster_: (booster_.finishTime if booster_.finishTime else NO_FUTURE_GIVEN, booster_.nextExpiryTime if booster_.nextExpiryTime else NO_FUTURE_GIVEN))
    boostersByResource = {}
    premiumBoosterArgsByResource = {}
    boosterCountByResource = {}
    setOfAlreadyRecorded = set()
    isInAccount = REQ_CRITERIA.BOOSTER.IN_ACCOUNT
    for booster in sortedBoostersList:
        showHint = controller is not None and booster.isExpirable and controller.shouldShowOnBoardingCardHint(booster.boosterID)
        resourceType = booster.boosterType
        if booster.boosterID in PREMIUM_BOOSTER_IDS:
            if booster.count != 0 or not (booster.isHidden or booster.isExpirable):
                if premiumBoosterArgsByResource.get(resourceType, None) is None:
                    premiumBoosterArgsByResource[resourceType] = BoosterModelData(resourceType=resourceType, category=category, booster=booster, depotCount=booster.count, showHint=showHint)
                else:
                    boosterData = premiumBoosterArgsByResource[resourceType]
                    updatedBoosterData = boosterData.replace(depotCount=boosterData.depotCount + booster.count)
                    premiumBoosterArgsByResource[resourceType] = updatedBoosterData
            continue
        if not isInAccount(booster):
            continue
        if resourceType not in setOfAlreadyRecorded:
            boostersByResource[resourceType] = booster
            setOfAlreadyRecorded.add(resourceType)
        count = boosterCountByResource.get(resourceType, 0)
        count += booster.count
        boosterCountByResource[resourceType] = count

    for resourceType in PERSONAL_RESOURCE_ORDER:
        booster = boostersByResource.get(resourceType, None)
        count = boosterCountByResource.get(resourceType, 0)
        showHint = controller is not None and booster is not None and booster.isExpirable and controller.shouldShowOnBoardingCardHint(booster.boosterID)
        nonPremiumBoosterArgs = BoosterModelData(resourceType=resourceType, category=category, booster=booster, depotCount=count, showHint=showHint)
        groupedBoosterModelDataByResourceType[resourceType] = [nonPremiumBoosterArgs]
        premiumBoosterArgs = premiumBoosterArgsByResource.get(resourceType)
        if premiumBoosterArgs is not None:
            groupedBoosterModelDataByResourceType[resourceType].append(premiumBoosterArgs)

    return groupedBoosterModelDataByResourceType


def addPersonalBoostersGroup(resourceType, boosterModelDataByType, groupArray):
    group = ReservesGroupModel()
    group.setCategory(RESERVE_GROUP_CATEGORY_LOOKUP[resourceType])
    boostersGroup = group.getReserves()
    for boosterModelData in boosterModelDataByType[resourceType]:
        addBoosterModel(boostersGroup, **boosterModelData._asdict())

    groupArray.addViewModel(group)


def addEventGroup(groupArray, cache):
    boosters = cache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_BOOSTER_ID_LIST(EVENT_BOOSTER_IDS))
    group = ReservesGroupModel()
    group.setCategory(GroupCategory.EVENT)
    boostersGroup = group.getReserves()
    for eventBoosterId in EVENT_BOOSTER_IDS:
        booster = boosters.get(eventBoosterId, None)
        if booster is None or not booster.isReadyToUse and booster.state == GOODIE_STATE.INACTIVE:
            continue
        addBoosterModel(boostersGroup, GOODIE_RESOURCE_TYPE.FL_XP, BoosterCategory.EVENT, booster, booster.count)

    if boostersGroup:
        groupArray.addViewModel(group)
    else:
        group.unbind()
    return


def addBoosterModel(boosterArray, resourceType, category, booster=None, depotCount=0, forcePremium=False, showHint=False):
    model = BoosterModel()
    isPremium = booster.getIsPremium() if booster else forcePremium
    model.setIsPremium(isPremium)
    iconId = getFullNameForBoosterIcon(resourceType, isPremium=isPremium)
    model.setIconId(iconId)
    model.setReserveType(BOOST_CATEGORY_TO_RESERVE_TYPE_LOOKUP[category])
    model.setInDepot(depotCount)
    model.setIsNew(showHint)
    if booster:
        boosterID = booster.boosterID
        model.setBoosterID(boosterID)
        model.setInactivationTime(makeLocalServerTime(booster.finishTime) or 0)
        model.setState(BOOSTER_STATE_TO_BOOSTER_MODEL_STATE[booster.state])
        model.setTotalDuration(booster.effectTime)
        model.setInDepotExpirableAmount(booster.getExpiringAmount())
        model.setIsExpiringSoon(0 < booster.getTimeLeftToNextExpiry() <= ONE_DAY)
        nearestExpiringTime, counter = getNearestExpirationTimeAndCountForToday((booster,))
        if nearestExpiringTime:
            model.setNextExpirationTime(nearestExpiringTime)
            model.setNextExpirationAmount(counter)
        if isinstance(booster, Booster):
            model.price.assign(booster.getBuyPrice())
        maxEffect, minEffect = makeBonuses(booster)
        model.setMinBonus(minEffect)
        model.setMaxBonus(maxEffect)
    boosterArray.addViewModel(model)


def makeBonuses(booster):
    bonus = booster.effectValue or [0]
    if isinstance(bonus, list):
        bonus = set(bonus)
        if len(bonus) > 1:
            return (max(bonus), min(bonus))
        bonus = bonus.pop()
    return (0, bonus)


def addToReserveArrayByCategory(reservesArray, boosters, category, cache, canAddEmpty=False):
    boosters = [ booster for booster in boosters if booster.category == category ]
    if not boosters and not canAddEmpty:
        return
    else:
        boostersByResourceType = {booster.boosterType:booster for booster in boosters}
        resourceTypeOrder = getGUIResourceOrder(category, boostersByResourceType)
        for resourceType in resourceTypeOrder:
            nextExpirationTime, nextExpirationAmount = getNearestExpiryTimeAndAmountByGroup(category, resourceType, cache)
            addBoosterModel(reservesArray, resourceType, category, booster=boostersByResourceType.get(resourceType, None), depotCount=getTotalBoostersByResourceType(category, resourceType, cache))
            model = reservesArray[-1]
            model.setNextExpirationTime(nextExpirationTime)
            model.setNextExpirationAmount(nextExpirationAmount)
            model.setInDepotExpirableAmount(getTotalLimitedBoostersByResourceType(category, resourceType, cache))

        return


def getReserveKind(boosterType):
    return ReserveKind(getBoosterGuiType(boosterType))


def fillBoosterModelWithData(model, booster):
    model.setIsPremium(booster.getIsPremium())
    model.setIconId(getFullNameForBoosterIcon(booster.boosterType, isPremium=booster.getIsPremium(), isExpirable=booster.isExpirable))
    model.setInDepot(booster.count)
    model.setInDepotExpirableAmount(booster.getExpiringAmount())
    model.setBoosterID(booster.boosterID)
    model.setReserveType(BOOST_CATEGORY_TO_RESERVE_TYPE_LOOKUP[booster.category])
    model.setReserveKind(getReserveKind(booster.boosterType))
    model.setInactivationTime(makeLocalServerTime(booster.finishTime) or 0)
    model.setState(BOOSTER_STATE_TO_BOOSTER_MODEL_STATE[booster.state])
    model.setTotalDuration(booster.effectTime)
    model.setNextExpirationTime(0)
    model.setNextExpirationAmount(0)
    if booster.expirations:
        expiry, expiryAmount = getNearestExpirationTimeAndCountForToday([booster])
        model.setNextExpirationTime(expiry)
        model.setNextExpirationAmount(expiryAmount)
    if isinstance(booster, Booster):
        if not booster.isHidden:
            model.price.assign(booster.getBuyPrice())
    maxEffect, minEffect = makeBonuses(booster)
    model.setMinBonus(minEffect)
    model.setMaxBonus(maxEffect)
