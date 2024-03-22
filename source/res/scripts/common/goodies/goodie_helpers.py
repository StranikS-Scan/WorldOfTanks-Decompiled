# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/goodie_helpers.py
from typing import TYPE_CHECKING, Type
from collections import namedtuple
from copy import deepcopy
from GoodieConditions import MaxVehicleLevel
from GoodieDefinition import GoodieDefinition
from GoodieResources import Gold, Credits, Experience, CrewExperience, FreeExperience, FrontlineExperience
from GoodieTargets import BuyPremiumAccount, BuySlot, PostBattle, BuyGoldTankmen, FreeExperienceConversion, BuyVehicle, EpicMeta, DemountOptionalDevice, EpicPostBattle, DropSkill
from goodie_multiple_resources import FreeXpCrewXpMultiResourceList, FreeXpMainXpMultiResourceList
from Goodies import GoodieException
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from goodie_constants import GOODIE_TARGET_TYPE, GOODIE_CONDITION_TYPE, GOODIE_RESOURCE_TYPE
if TYPE_CHECKING:
    from typing import Tuple, Dict, Optional
    from goodies.Goodies import Goodies
    from goodies.GoodieResources import GoodieResourceType
GoodieData = namedtuple('GoodieData', ['variety',
 'target',
 'enabled',
 'lifetime',
 'useby',
 'counter',
 'autostart',
 'condition',
 'resource',
 'expireAfter',
 'roundToEndOfGameDay'])
GoodieExpirationData = namedtuple('GoodieExpirationData', ['booster', 'timestamp', 'amount'])
_CONDITIONS = {GOODIE_CONDITION_TYPE.MAX_VEHICLE_LEVEL: MaxVehicleLevel}
_TARGETS = {GOODIE_TARGET_TYPE.ON_BUY_PREMIUM: BuyPremiumAccount,
 GOODIE_TARGET_TYPE.ON_BUY_SLOT: BuySlot,
 GOODIE_TARGET_TYPE.ON_POST_BATTLE: PostBattle,
 GOODIE_TARGET_TYPE.ON_BUY_GOLD_TANKMEN: BuyGoldTankmen,
 GOODIE_TARGET_TYPE.ON_FREE_XP_CONVERSION: FreeExperienceConversion,
 GOODIE_TARGET_TYPE.ON_BUY_VEHICLE: BuyVehicle,
 GOODIE_TARGET_TYPE.ON_EPIC_META: EpicMeta,
 GOODIE_TARGET_TYPE.ON_DEMOUNT_OPTIONAL_DEVICE: DemountOptionalDevice,
 GOODIE_TARGET_TYPE.EPIC_POST_BATTLE: EpicPostBattle,
 GOODIE_TARGET_TYPE.ON_DROP_SKILL: DropSkill}
RESOURCES = {GOODIE_RESOURCE_TYPE.GOLD: Gold,
 GOODIE_RESOURCE_TYPE.CREDITS: Credits,
 GOODIE_RESOURCE_TYPE.XP: Experience,
 GOODIE_RESOURCE_TYPE.CREW_XP: CrewExperience,
 GOODIE_RESOURCE_TYPE.FREE_XP: FreeExperience,
 GOODIE_RESOURCE_TYPE.FL_XP: FrontlineExperience,
 GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP: FreeXpCrewXpMultiResourceList,
 GOODIE_RESOURCE_TYPE.FREE_XP_MAIN_XP: FreeXpMainXpMultiResourceList}
RESOURCE_TO_GOODIE_LOOKUP = {resource:goodieType for goodieType, resource in RESOURCES.iteritems()}
GOODIE_CONDITION_TO_TEXT = {MaxVehicleLevel: 'max_vehicle_level'}
GOODIE_RESOURCE_TO_TEXT = {Gold: 'gold',
 Credits: 'credits',
 Experience: 'experience',
 CrewExperience: 'crew_experience',
 FreeExperience: 'free_experience',
 FrontlineExperience: 'fl_experience',
 FreeXpCrewXpMultiResourceList: 'free_xp_and_crew_xp'}
GOODIE_TARGET_TO_TEXT = {BuyPremiumAccount: 'premium',
 BuySlot: 'slot',
 PostBattle: 'post_battle',
 BuyGoldTankmen: 'gold_tankmen',
 FreeExperienceConversion: 'free_xp_conversion',
 BuyVehicle: 'vehicle',
 EpicMeta: 'epic_meta',
 DemountOptionalDevice: 'demount_optional_device',
 EpicPostBattle: 'epic_post_battle',
 DropSkill: 'drop_skill'}
GOODIE_TEXT_TO_CONDITION = {'max_vehicle_level': GOODIE_CONDITION_TYPE.MAX_VEHICLE_LEVEL}
GOODIE_TEXT_TO_RESOURCE = {'credits': GOODIE_RESOURCE_TYPE.CREDITS,
 'experience': GOODIE_RESOURCE_TYPE.XP,
 'crew_experience': GOODIE_RESOURCE_TYPE.CREW_XP,
 'free_experience': GOODIE_RESOURCE_TYPE.FREE_XP,
 'gold': GOODIE_RESOURCE_TYPE.GOLD,
 'fl_experience': GOODIE_RESOURCE_TYPE.FL_XP,
 'free_xp_and_crew_xp': GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP,
 'free_xp_and_main_xp': GOODIE_RESOURCE_TYPE.FREE_XP_MAIN_XP}
GOODIE_TEXT_TO_TARGET = {'premium': GOODIE_TARGET_TYPE.ON_BUY_PREMIUM,
 'slot': GOODIE_TARGET_TYPE.ON_BUY_SLOT,
 'post_battle': GOODIE_TARGET_TYPE.ON_POST_BATTLE,
 'gold_tankmen': GOODIE_TARGET_TYPE.ON_BUY_GOLD_TANKMEN,
 'free_xp_conversion': GOODIE_TARGET_TYPE.ON_FREE_XP_CONVERSION,
 'vehicle': GOODIE_TARGET_TYPE.ON_BUY_VEHICLE,
 'epic_meta': GOODIE_TARGET_TYPE.ON_EPIC_META,
 'demount_optional_device': GOODIE_TARGET_TYPE.ON_DEMOUNT_OPTIONAL_DEVICE,
 'epic_post_battle': GOODIE_TARGET_TYPE.EPIC_POST_BATTLE,
 'drop_skill': GOODIE_TARGET_TYPE.ON_DROP_SKILL}
CURRENCY_TO_RESOURCE_TYPE = {'gold': GOODIE_RESOURCE_TYPE.GOLD,
 'credits': GOODIE_RESOURCE_TYPE.CREDITS}
CURRENCY_TO_RESOURCE = {k:RESOURCES[v] for k, v in CURRENCY_TO_RESOURCE_TYPE.iteritems()}

def loadDefinitions(d):
    goodies = {'goodies': {},
     'prices': deepcopy(d['prices']),
     'notInShop': deepcopy(d['notInShop'])}
    for uid, d in d['goodies'].iteritems():
        v_variety, v_target, v_enabled, v_lifetime, v_useby, v_limit, v_autostart, v_condition, v_resource, v_expireAfter, v_roundToEndOfGameDay = d
        if v_condition is not None:
            condition = _CONDITIONS.get(v_condition[0])(v_condition[1])
        else:
            condition = None
        target = _TARGETS[v_target[0]](v_target[1], v_target[2])
        resource = RESOURCES[v_resource[0]]
        value = resource.provideCompatibleValueDescr(actualVal=v_resource[1], isPercent=v_resource[2])
        goodies['goodies'][uid] = GoodieDefinition(uid=uid, variety=v_variety, target=target, enabled=v_enabled, lifetime=v_lifetime, useby=v_useby, counter=v_limit, autostart=v_autostart, resource=resource, value=value, condition=condition, expireAfter=v_expireAfter, roundToEndOfGameDay=v_roundToEndOfGameDay)

    return goodies


def getPriceWithDiscount(price, resourceData):
    _, value, isPercentage = resourceData
    if isPercentage:
        result = int(price - price * (value / float(100)))
        if result < 0:
            return 0
        else:
            return result
    else:
        return max(price - value, 0)


def getPremiumCost(premiumCosts, goodie):
    if goodie.target[0] == GOODIE_TARGET_TYPE.ON_BUY_PREMIUM:
        price = premiumCosts.get(goodie.getTargetValue(), None)
        if price is None:
            return
        return getPriceWithDiscount(price, goodie.resource)
    else:
        return


def loadPdata(pdataGoodies, goodies, logID):
    for uid, (status, finishTime, count, expirations) in pdataGoodies.iteritems():
        try:
            goodies.load(uid, status, finishTime, count, expirations)
        except GoodieException as detail:
            LOG_CURRENT_EXCEPTION()
            LOG_ERROR('Cannot load a goodie', detail, logID)


def calcDefaultPrice(default, actual):
    result = {}
    defaultPrices = default['prices']
    actualPrices = actual['prices']
    for goodieID, defaultPrice in defaultPrices.iteritems():
        actualPrice = actualPrices.get(goodieID, None)
        if actualPrice is None:
            continue
        changedCredits = changedGold = 0
        if defaultPrice[0] > actualPrice[0]:
            changedCredits = defaultPrice[0] - actualPrice[0]
        if defaultPrice[1] > actualPrice[1]:
            changedGold = defaultPrice[1] - actualPrice[1]
        if changedCredits or changedGold:
            result[goodieID] = (changedCredits, changedGold)

    return result


def wipe(goodies, pdata, leaveGold):
    if leaveGold:
        for goodieID in pdata['goodies'].keys():
            price = goodies['prices'].get(goodieID, None)
            if price is not None and price[0] != 0:
                del pdata['goodies'][goodieID]

    else:
        pdata['goodies'].clear()
    if 'pr2_conversion' in pdata:
        del pdata['pr2_conversion']
    return
