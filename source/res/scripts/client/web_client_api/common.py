# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/common.py
from collections import namedtuple
from shared_utils import CONST_CONTAINER
ItemPackEntry = namedtuple('ItemPackEntry', ('type', 'id', 'count', 'groupID', 'compensation', 'iconSource', 'title', 'description'))
ItemPackEntry.__new__.__defaults__ = (None, None, None, None, None, None, '', '')

class ShopItemType(CONST_CONTAINER):
    VEHICLE = 'vehicle'
    EQUIPMENT = 'equipment'
    DEVICE = 'device'
    BOOSTER = 'booster'
    BATTLE_BOOSTER = 'battleBooster'
    MODULE = 'module'
    SHELL = 'shell'
    PREMIUM = 'premium'


class ItemPackType(CONST_CONTAINER):
    ITEM_SHELL = 'item/shell'
    ITEM_DEVICE = 'item/optionalDevice'
    ITEM_EQUIPMENT = 'item/equipment'
    VEHICLE_HEAVY = 'vehicle/heavyTank'
    VEHICLE_AT_SPG = 'vehicle/AT-SPG'
    VEHICLE_MEDIUM = 'vehicle/mediumTank'
    VEHICLE_LIGHT = 'vehicle/lightTank'
    VEHICLE_SPG = 'vehicle/SPG'
    VEHICLE = 'vehicle'
    GOODIE_GOLD = 'goodie/gold'
    GOODIE_CREDITS = 'goodie/credits'
    GOODIE_EXPERIENCE = 'goodie/experience'
    GOODIE_FREE_EXPERIENCE = 'goodie/free_experience'
    GOODIE_CREW_EXPERIENCE = 'goodie/crew_experience'
    GOODIE = 'goodie'
    CAMOUFLAGE_WINTER = 'camouflage/winter'
    CAMOUFLAGE_SUMMER = 'camouflage/summer'
    CAMOUFLAGE_DESERT = 'camouflage/desert'
    CAMOUFLAGE = 'camouflage'
    STYLE = 'style'
    DECAL_1 = 'decal/1'
    DECAL_2 = 'decal/2'
    DECAL = 'decal'
    MODIFICATION = 'modification'
    PAINT_WINTER = 'paint/winter'
    PAINT_SUMMER = 'paint/summer'
    PAINT_DESERT = 'paint/desert'
    PAINT = 'paint'
    CUSTOM_GOLD = 'custom/gold'
    CUSTOM_PREMIUM = 'custom/premium'
    CUSTOM_CREDITS = 'custom/credits'
    CUSTOM_CRYSTAL = 'custom/crystal'
    CUSTOM_SLOT = 'custom/slot'
    CREW_50 = 'crew/50'
    CREW_75 = 'crew/75'
    CREW_100 = 'crew/100'
    TOKEN = 'token'


class ItemPackTypeGroup(CONST_CONTAINER):
    ITEM = (ItemPackType.ITEM_SHELL, ItemPackType.ITEM_DEVICE, ItemPackType.ITEM_EQUIPMENT)
    VEHICLE = (ItemPackType.VEHICLE,
     ItemPackType.VEHICLE_SPG,
     ItemPackType.VEHICLE_AT_SPG,
     ItemPackType.VEHICLE_HEAVY,
     ItemPackType.VEHICLE_MEDIUM,
     ItemPackType.VEHICLE_LIGHT)
    GOODIE = (ItemPackType.GOODIE,
     ItemPackType.GOODIE_GOLD,
     ItemPackType.GOODIE_CREDITS,
     ItemPackType.GOODIE_EXPERIENCE,
     ItemPackType.GOODIE_CREW_EXPERIENCE,
     ItemPackType.GOODIE_FREE_EXPERIENCE)
    CAMOUFLAGE = (ItemPackType.CAMOUFLAGE,
     ItemPackType.CAMOUFLAGE_DESERT,
     ItemPackType.CAMOUFLAGE_SUMMER,
     ItemPackType.CAMOUFLAGE_WINTER)
    PAINT = (ItemPackType.PAINT,
     ItemPackType.PAINT_DESERT,
     ItemPackType.PAINT_SUMMER,
     ItemPackType.PAINT_WINTER)
    STYLE = (ItemPackType.STYLE,)
    MODIFICATION = (ItemPackType.MODIFICATION,)
    DECAL = (ItemPackType.DECAL, ItemPackType.DECAL_1, ItemPackType.DECAL_2)
    CUSTOM = (ItemPackType.CUSTOM_PREMIUM,
     ItemPackType.CUSTOM_CRYSTAL,
     ItemPackType.CUSTOM_GOLD,
     ItemPackType.CUSTOM_CREDITS,
     ItemPackType.CUSTOM_SLOT)
    CREW = (ItemPackType.CREW_50, ItemPackType.CREW_75, ItemPackType.CREW_100)
    TOKEN = (ItemPackType.TOKEN,)


CompensationSpec = namedtuple('CompensationSpec', ('type', 'value', 'count'))

class CompensationType(CONST_CONTAINER):
    MONEY = 'money'
