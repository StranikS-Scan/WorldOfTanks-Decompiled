# Embedded file name: scripts/common/goodies/goodie_helpers.py
from collections import namedtuple
from GoodieConditions import MaxVehicleLevel
from GoodieDefinition import GoodieDefinition
from GoodieResources import Gold, Credits, Experience, CrewExperience, FreeExperience
from GoodieTargets import BuyPremiumAccount, BuySlot, PostBattle
from GoodieValue import GoodieValue
from goodie_constants import GOODIE_TARGET_TYPE, GOODIE_CONDITION_TYPE, GOODIE_RESOURCE_TYPE
GoodieData = namedtuple('GoodieData', 'variety target enabled lifetime useby limit autostart condition resources')
_CONDITIONS = {GOODIE_CONDITION_TYPE.MAX_VEHICLE_LEVEL: MaxVehicleLevel}
_TARGETS = {GOODIE_TARGET_TYPE.ON_BUY_PREMIUM: BuyPremiumAccount,
 GOODIE_TARGET_TYPE.ON_BUY_SLOT: BuySlot,
 GOODIE_TARGET_TYPE.ON_POST_BATTLE: PostBattle}
_RESOURCES = {GOODIE_RESOURCE_TYPE.GOLD: Gold,
 GOODIE_RESOURCE_TYPE.CREDITS: Credits,
 GOODIE_RESOURCE_TYPE.XP: Experience,
 GOODIE_RESOURCE_TYPE.CREW_XP: CrewExperience,
 GOODIE_RESOURCE_TYPE.FREE_XP: FreeExperience}

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
        v_variety = d[0]
        v_target = d[1]
        v_enabled = d[2]
        v_lifetime = d[3]
        v_useby = d[4]
        v_limit = d[5]
        v_autostart = d[6]
        v_condition = d[7]
        v_resources = d[8]
        if v_condition is not None:
            condition = _CONDITIONS.get(v_condition[0])(v_condition[1])
        else:
            condition = None
        target = _TARGETS[v_target[0]](v_target[1])
        resources = {}
        for r in v_resources:
            if r[2]:
                resources[_RESOURCES[r[0]]] = GoodieValue.percent(r[1])
            else:
                resources[_RESOURCES[r[0]]] = GoodieValue.absolute(r[1])

        goodies[uid] = GoodieDefinition(uid=uid, variety=v_variety, target=target, enabled=v_enabled, lifetime=v_lifetime, useby=v_useby, counter=v_limit, autostart=v_autostart, resources=resources, condition=condition)

    return goodies


def getPremiumCost(premiumCosts, goodie):
    if goodie.target[0] == GOODIE_TARGET_TYPE.ON_BUY_PREMIUM:
        price = premiumCosts.get(goodie.getTargetValue(), None)
        if price is None:
            return
        value = goodie.resources[0]
        if value[2]:
            result = int(price - price * (value[1] / float(100)))
            if result < 0:
                return 0
            else:
                return result
        else:
            return price - value[1]
    else:
        return
    return


def loadPdata(pdataGoodies, goodies):
    for uid, goodie in pdataGoodies.iteritems():
        goodies.load(uid, goodie[0], goodie[1], goodie[2])
