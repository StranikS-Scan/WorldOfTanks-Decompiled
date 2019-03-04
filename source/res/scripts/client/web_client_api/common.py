# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/common.py
from collections import namedtuple
from gui.shared.money import MONEY_UNDEFINED
from shared_utils import CONST_CONTAINER
VehicleOfferEntry = namedtuple('VehicleOfferEntry', ('id', 'eventType', 'rent', 'crew', 'name', 'label', 'left', 'buyPrice', 'bestOffer', 'buyParams', 'preferred'))
VehicleOfferEntry.__new__.__defaults__ = ('',
 None,
 None,
 None,
 'Unnamed',
 'Unnamed',
 (),
 MONEY_UNDEFINED,
 None,
 None,
 False)
ItemPackEntry = namedtuple('ItemPackEntry', ('type', 'id', 'count', 'groupID', 'compensation', 'iconSource', 'title', 'description', 'extra'))
ItemPackEntry.__new__.__defaults__ = (None, None, None, None, None, None, '', '', None)

class ShopItemType(CONST_CONTAINER):
    VEHICLE = 'vehicle'
    EQUIPMENT = 'equipment'
    DEVICE = 'device'
    BOOSTER = 'booster'
    BATTLE_BOOSTER = 'battleBooster'
    MODULE = 'module'
    SHELL = 'shell'
    PREMIUM = 'premium'
    PAINT = 'paint'
    CAMOUFLAGE = 'camouflage'
    MODIFICATION = 'modification'
    STYLE = 'style'
    DECAL = 'decal'
    EMBLEM = 'emblem'
    INSCRIPTION = 'inscription'
    PROJECTION_DECAL = 'projectionDecal'


class ItemPackType(CONST_CONTAINER):
    VEHICLE_LIGHT = 'vehicle/lightTank'
    VEHICLE_MEDIUM = 'vehicle/mediumTank'
    VEHICLE_HEAVY = 'vehicle/heavyTank'
    VEHICLE_AT_SPG = 'vehicle/AT-SPG'
    VEHICLE_SPG = 'vehicle/SPG'
    ITEM_EQUIPMENT = 'item/equipment'
    ITEM_DEVICE = 'item/optionalDevice'
    ITEM_SHELL = 'item/shell'
    ITEM_BATTLE_BOOSTER = 'item/battleBooster'
    GOODIE_GOLD = 'goodie/gold'
    GOODIE_CREDITS = 'goodie/credits'
    GOODIE_EXPERIENCE = 'goodie/experience'
    GOODIE_FREE_EXPERIENCE = 'goodie/free_experience'
    GOODIE_CREW_EXPERIENCE = 'goodie/crew_experience'
    CREW_50 = 'crew/50'
    CREW_75 = 'crew/75'
    CREW_100 = 'crew/100'
    CREW_CUSTOM = 'crew/custom'
    CUSTOM_PREMIUM = 'custom/premium'
    CUSTOM_CRYSTAL = 'custom/crystal'
    CUSTOM_GOLD = 'custom/gold'
    CUSTOM_CREDITS = 'custom/credits'
    CUSTOM_SLOT = 'custom/slot'
    CUSTOM_REFERRAL_CREW = 'custom/crew'
    CUSTOM_REWARD_POINT = 'custom/prestige_point'
    CUSTOM_SUPPLY_POINT = 'custom/supply_point'
    TOKEN = 'token'
    PAINT_ALL = 'paint/all'
    PAINT_SUMMER = 'paint/summer'
    PAINT_WINTER = 'paint/winter'
    PAINT_DESERT = 'paint/desert'
    CAMOUFLAGE_ALL = 'camouflage/all'
    CAMOUFLAGE_SUMMER = 'camouflage/summer'
    CAMOUFLAGE_WINTER = 'camouflage/winter'
    CAMOUFLAGE_DESERT = 'camouflage/desert'
    DECAL_1 = 'decal/1'
    DECAL_2 = 'decal/2'
    MODIFICATION = 'modification'
    STYLE = 'style'
    ACHIEVEMENT = 'achievement'
    BADGE = 'badge'
    REFERRAL_BADGE = 'referralBadge'
    PLAYER_BADGE = 'playerBadges'
    SINGLE_ACHIEVEMENTS = 'singleAchievements'


class ItemPackTypeGroup(CONST_CONTAINER):
    ITEM = (ItemPackType.ITEM_SHELL,
     ItemPackType.ITEM_DEVICE,
     ItemPackType.ITEM_EQUIPMENT,
     ItemPackType.ITEM_BATTLE_BOOSTER)
    VEHICLE = (ItemPackType.VEHICLE_SPG,
     ItemPackType.VEHICLE_AT_SPG,
     ItemPackType.VEHICLE_HEAVY,
     ItemPackType.VEHICLE_MEDIUM,
     ItemPackType.VEHICLE_LIGHT)
    GOODIE = (ItemPackType.GOODIE_GOLD,
     ItemPackType.GOODIE_CREDITS,
     ItemPackType.GOODIE_EXPERIENCE,
     ItemPackType.GOODIE_CREW_EXPERIENCE,
     ItemPackType.GOODIE_FREE_EXPERIENCE)
    CAMOUFLAGE = (ItemPackType.CAMOUFLAGE_ALL,
     ItemPackType.CAMOUFLAGE_DESERT,
     ItemPackType.CAMOUFLAGE_SUMMER,
     ItemPackType.CAMOUFLAGE_WINTER)
    PAINT = (ItemPackType.PAINT_ALL,
     ItemPackType.PAINT_DESERT,
     ItemPackType.PAINT_SUMMER,
     ItemPackType.PAINT_WINTER)
    STYLE = (ItemPackType.STYLE,)
    MODIFICATION = (ItemPackType.MODIFICATION,)
    DECAL = (ItemPackType.DECAL_1, ItemPackType.DECAL_2)
    CUSTOM = (ItemPackType.CUSTOM_PREMIUM,
     ItemPackType.CUSTOM_CRYSTAL,
     ItemPackType.CUSTOM_GOLD,
     ItemPackType.CUSTOM_CREDITS,
     ItemPackType.CUSTOM_REFERRAL_CREW,
     ItemPackType.CUSTOM_SLOT,
     ItemPackType.CUSTOM_REWARD_POINT,
     ItemPackType.CUSTOM_SUPPLY_POINT)
    CREW = (ItemPackType.CREW_50,
     ItemPackType.CREW_75,
     ItemPackType.CREW_100,
     ItemPackType.CREW_CUSTOM)
    TOKEN = (ItemPackType.TOKEN,)


CompensationSpec = namedtuple('CompensationSpec', ('type', 'value', 'count'))

class CompensationType(CONST_CONTAINER):
    MONEY = 'money'
