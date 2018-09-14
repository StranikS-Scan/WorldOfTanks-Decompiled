# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/goodie_helpers.py
from collections import namedtuple
from GoodieConditions import MaxVehicleLevel
from GoodieDefinition import GoodieDefinition
from GoodieResources import Gold, Credits, Experience, CrewExperience, FreeExperience
from GoodieTargets import BuyPremiumAccount, BuySlot, PostBattle, BuyGoldTankmen, FreeExperienceConversion
from GoodieValue import GoodieValue
from goodie_constants import GOODIE_TARGET_TYPE, GOODIE_CONDITION_TYPE, GOODIE_RESOURCE_TYPE
GoodieData = namedtuple('GoodieData', 'variety target enabled lifetime useby limit autostart condition resource')
_CONDITIONS = {GOODIE_CONDITION_TYPE.MAX_VEHICLE_LEVEL: MaxVehicleLevel}
_TARGETS = {GOODIE_TARGET_TYPE.ON_BUY_PREMIUM: BuyPremiumAccount,
 GOODIE_TARGET_TYPE.ON_BUY_SLOT: BuySlot,
 GOODIE_TARGET_TYPE.ON_POST_BATTLE: PostBattle,
 GOODIE_TARGET_TYPE.ON_BUY_GOLD_TANKMEN: BuyGoldTankmen,
 GOODIE_TARGET_TYPE.ON_FREE_XP_CONVERSION: FreeExperienceConversion}
_RESOURCES = {GOODIE_RESOURCE_TYPE.GOLD: Gold,
 GOODIE_RESOURCE_TYPE.CREDITS: Credits,
 GOODIE_RESOURCE_TYPE.XP: Experience,
 GOODIE_RESOURCE_TYPE.CREW_XP: CrewExperience,
 GOODIE_RESOURCE_TYPE.FREE_XP: FreeExperience}
GOODIE_CONDITION_TO_TEXT = {MaxVehicleLevel: 'max_vehicle_level'}
GOODIE_RESOURCE_TO_TEXT = {Gold: 'gold',
 Credits: 'credits',
 Experience: 'experience',
 CrewExperience: 'crew_experience',
 FreeExperience: 'free_experience'}
GOODIE_TARGET_TO_TEXT = {BuyPremiumAccount: 'premium',
 BuySlot: 'slot',
 PostBattle: 'post_battle',
 BuyGoldTankmen: 'gold_tankmen',
 FreeExperienceConversion: 'free_xp_conversion'}
GOODIE_TEXT_TO_CONDITION = {'max_vehicle_level': GOODIE_CONDITION_TYPE.MAX_VEHICLE_LEVEL}
GOODIE_TEXT_TO_RESOURCE = {'credits': GOODIE_RESOURCE_TYPE.CREDITS,
 'experience': GOODIE_RESOURCE_TYPE.XP,
 'crew_experience': GOODIE_RESOURCE_TYPE.CREW_XP,
 'free_experience': GOODIE_RESOURCE_TYPE.FREE_XP,
 'gold': GOODIE_RESOURCE_TYPE.GOLD}
GOODIE_TEXT_TO_TARGET = {'premium': GOODIE_TARGET_TYPE.ON_BUY_PREMIUM,
 'slot': GOODIE_TARGET_TYPE.ON_BUY_SLOT,
 'post_battle': GOODIE_TARGET_TYPE.ON_POST_BATTLE,
 'gold_tankmen': GOODIE_TARGET_TYPE.ON_BUY_GOLD_TANKMEN,
 'free_xp_conversion': GOODIE_TARGET_TYPE.ON_FREE_XP_CONVERSION}

class NamedGoodieData(GoodieData):

    def getTargetValue(self):
        if self.target[0] == GOODIE_TARGET_TYPE.ON_BUY_PREMIUM:
            return int(self.target[1].split('_')[1])
        else:
            return self.target[1]

    @property
    def targetID(self):
        return self.target[0]


def loadDefinitions(d):
    goodies = {}
    for uid, d in d.iteritems():
        v_variety, v_target, v_enabled, v_lifetime, v_useby, v_limit, v_autostart, v_condition, v_resource = d
        if v_condition is not None:
            condition = _CONDITIONS.get(v_condition[0])(v_condition[1])
        else:
            condition = None
        target = _TARGETS[v_target[0]](v_target[1], v_target[2])
        resource = _RESOURCES[v_resource[0]]
        if v_resource[2]:
            value = GoodieValue.percent(v_resource[1])
        else:
            value = GoodieValue.absolute(v_resource[1])
        goodies[uid] = GoodieDefinition(uid=uid, variety=v_variety, target=target, enabled=v_enabled, lifetime=v_lifetime, useby=v_useby, counter=v_limit, autostart=v_autostart, resource=resource, value=value, condition=condition)

    return goodies


def getPriceWithDiscount(price, value):
    if value[2]:
        result = int(price - price * (value[1] / float(100)))
        if result < 0:
            return 0
        else:
            return result
    else:
        return price - value[1]


def getPremiumCost(premiumCosts, goodie):
    if goodie.target[0] == GOODIE_TARGET_TYPE.ON_BUY_PREMIUM:
        price = premiumCosts.get(goodie.getTargetValue(), None)
        if price is None:
            return
        return getPriceWithDiscount(price, goodie.resource)
    else:
        return


def loadPdata(pdataGoodies, goodies):
    for uid, goodie in pdataGoodies.iteritems():
        goodies.load(uid, goodie[0], goodie[1], goodie[2])
