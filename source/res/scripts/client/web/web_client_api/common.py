# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/common.py
import itertools
from collections import namedtuple
from enum import Enum, unique
from gui.shared.money import MONEY_UNDEFINED
from shared_utils import CONST_CONTAINER
SPA_ID_TYPES = (int, long)
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
ItemPackEntry.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 '',
 '',
 {})

class _Enum(Enum):

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_


@unique
class TManLocation(_Enum):
    NEWBIES = 'newbies'
    BARRACKS = 'barracks'
    TANKS = 'tanks'
    DEMOBILIZED = 'demobilized'


@unique
class TManGender(_Enum):
    MALE = 'male'
    FEMALE = 'female'


class ShopItemType(CONST_CONTAINER):
    VEHICLE = 'vehicle'
    CREW = 'crew'
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
    ENHANCEMENT = 'enhancements'
    CREW_BOOKS = 'crew_books'


class ItemPackType(CONST_CONTAINER):
    VEHICLE = 'vehicle'
    VEHICLE_LIGHT = 'vehicle/lightTank'
    VEHICLE_MEDIUM = 'vehicle/mediumTank'
    VEHICLE_HEAVY = 'vehicle/heavyTank'
    VEHICLE_AT_SPG = 'vehicle/AT-SPG'
    VEHICLE_SPG = 'vehicle/SPG'
    ITEM_EQUIPMENT = 'item/equipment'
    ITEM_DEVICE = 'item/optionalDevice'
    ITEM_SHELL = 'item/shell'
    ITEM_CREW_SKIN = 'item/crewSkin'
    GOODIE_GOLD = 'goodie/gold'
    GOODIE_CREDITS = 'goodie/credits'
    GOODIE_EXPERIENCE = 'goodie/experience'
    GOODIE_FREE_EXPERIENCE = 'goodie/free_experience'
    GOODIE_CREW_EXPERIENCE = 'goodie/crew_experience'
    GOODIE_FREE_AND_CREW_EXPERIENCE = 'goodie/free_xp_and_crew_xp'
    GOODIE_FRONTLINE_EXPERIENCE = 'goodie/fl_experience'
    GOODIE_RECERTIFICATIONFORM = 'goodie/recertificationForm'
    CREW_50 = 'crew/50'
    CREW_75 = 'crew/75'
    CREW_100 = 'crew/100'
    CUSTOM_CREW_100 = 'custom_crew/100'
    CREW_BUNDLE = 'crew/bundle'
    CREW_CUSTOM = 'crew/custom'
    CUSTOM_PREMIUM = 'custom/premium'
    CUSTOM_PREMIUM_PLUS = 'custom/premium_plus'
    CUSTOM_CRYSTAL = 'custom/crystal'
    CUSTOM_GOLD = 'custom/gold'
    CUSTOM_CREDITS = 'custom/credits'
    CUSTOM_FREE_XP = 'custom/freeXP'
    CUSTOM_DOG_TAG = 'custom/dogTagComponents'
    CUSTOM_EVENT_COIN = 'custom/eventCoin'
    CUSTOM_EVENT_COIN_EXTERNAL = 'custom/event_coin'
    CUSTOM_BPCOIN = 'custom/bpcoin'
    CUSTOM_EQUIP_COIN = 'custom/equip_coin'
    CUSTOM_SLOT = 'custom/slot'
    CUSTOM_SEVERAL_SLOTS = 'custom/slots'
    CUSTOM_REFERRAL_CREW = 'custom/crew'
    CUSTOM_SUPPLY_POINT = 'custom/supply_point'
    CUSTOM_BATTLE_PASS_POINTS = 'custom/battlePassPoints'
    CUSTOM_X5_BATTLE_BONUS = 'custom/X5_battle'
    CUSTOM_COLLECTION_ENTITLEMENT = 'custom/collectionItem'
    CUSTOM_ANY_COLLECTION_ITEM = 'custom/anyCollectionItem'
    CUSTOM_X3_CREW_BONUS = 'custom/X3_crew'
    CUSTOM_LOOTBOX = 'custom/lootbox'
    CUSTOM_LOOTBOXKEY = 'custom/LootBoxKey'
    CUSTOM_BERTHS = 'custom/berths'
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
    PROJECTION_DECAL = 'projection_decal/all'
    PERSONAL_NUMBER = 'personal_number/all'
    MODIFICATION = 'modification/all'
    STYLE = 'style/all'
    ACHIEVEMENT = 'achievement'
    BADGE = 'badge'
    REFERRAL_BADGE = 'referralBadge'
    PLAYER_BADGE = 'playerBadges'
    SINGLE_ACHIEVEMENTS = 'singleAchievements'
    FRONTLINE_TOKEN = 'frontline_token'
    TRADE_IN_INFO = 'tradeInInfo'
    CREW_BOOK = 'crewBook'
    CREW_BOOK_BROCHURE = 'crew_book/brochure'
    CREW_BOOK_GUIDE = 'crew_book/guide'
    CREW_BOOK_CREW_BOOK = 'crew_book/crewBook'
    CREW_BOOK_PERSONAL_BOOK = 'crew_book/personalBook'
    CREW_BOOK_UNIVERSAL_BOOK = 'crew_book/universalBook'
    CREW_BOOK_RANDOM = 'crew_book/random'
    CREW_BOOK_UNIVERSAL_GUIDE = 'crew_book/universalGuide'
    CREW_BOOK_UNIVERSAL_BROCHURE = 'crew_book/universalBrochure'
    BLUEPRINT = 'blueprint'
    BLUEPRINT_NATIONAL = 'blueprint/national'
    BLUEPRINT_INTELEGENCE_DATA = 'blueprint/intelligence_data'
    BLUEPRINT_ANY = 'blueprint/any'
    BLUEPRINT_NATIONAL_ANY = 'blueprint/nationalAny'
    DEMOUNT_KIT = 'demountKit'
    REFERRAL_AWARDS = 'referral_awards'
    DEMOUNT_KITS = 'demountKit/common'
    OFFER = 'offer'
    OFFER_BROCHURE = 'offer/crew_book/brochure'
    OFFER_BATTLE_BOOSTER = 'offer/item/equipment'
    TMAN_TOKEN = 'tmanToken'


class ItemPackTypeGroup(CONST_CONTAINER):
    ITEM = (ItemPackType.ITEM_SHELL, ItemPackType.ITEM_DEVICE, ItemPackType.ITEM_EQUIPMENT)
    VEHICLE = (ItemPackType.VEHICLE,
     ItemPackType.VEHICLE_SPG,
     ItemPackType.VEHICLE_AT_SPG,
     ItemPackType.VEHICLE_HEAVY,
     ItemPackType.VEHICLE_MEDIUM,
     ItemPackType.VEHICLE_LIGHT)
    GOODIE = (ItemPackType.GOODIE_GOLD,
     ItemPackType.GOODIE_CREDITS,
     ItemPackType.GOODIE_EXPERIENCE,
     ItemPackType.GOODIE_CREW_EXPERIENCE,
     ItemPackType.GOODIE_FREE_EXPERIENCE,
     ItemPackType.GOODIE_FREE_AND_CREW_EXPERIENCE,
     ItemPackType.GOODIE_FRONTLINE_EXPERIENCE)
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
    PROJECTION_DECAL = (ItemPackType.PROJECTION_DECAL,)
    PERSONAL_NUMBER = (ItemPackType.PERSONAL_NUMBER,)
    CUSTOMIZATION = tuple(itertools.chain(STYLE, CAMOUFLAGE, PAINT, DECAL, PROJECTION_DECAL, PERSONAL_NUMBER, MODIFICATION))
    CUSTOM = (ItemPackType.CUSTOM_PREMIUM,
     ItemPackType.CUSTOM_PREMIUM_PLUS,
     ItemPackType.CUSTOM_CRYSTAL,
     ItemPackType.CUSTOM_GOLD,
     ItemPackType.CUSTOM_CREDITS,
     ItemPackType.CUSTOM_EVENT_COIN,
     ItemPackType.CUSTOM_EVENT_COIN_EXTERNAL,
     ItemPackType.CUSTOM_REFERRAL_CREW,
     ItemPackType.CUSTOM_SLOT,
     ItemPackType.CUSTOM_SUPPLY_POINT)
    CREW = (ItemPackType.CREW_50,
     ItemPackType.CREW_75,
     ItemPackType.CREW_100,
     ItemPackType.CUSTOM_CREW_100,
     ItemPackType.CREW_BUNDLE,
     ItemPackType.CREW_CUSTOM)
    TOKEN = (ItemPackType.TOKEN,)
    DISCOUNT = (ItemPackType.FRONTLINE_TOKEN,)
    TRADE_IN = (ItemPackType.TRADE_IN_INFO,)
    CREW_BOOKS = (ItemPackType.CREW_BOOK,
     ItemPackType.CREW_BOOK_BROCHURE,
     ItemPackType.CREW_BOOK_GUIDE,
     ItemPackType.CREW_BOOK_CREW_BOOK,
     ItemPackType.CREW_BOOK_PERSONAL_BOOK,
     ItemPackType.CREW_BOOK_UNIVERSAL_BOOK,
     ItemPackType.CREW_BOOK_UNIVERSAL_GUIDE,
     ItemPackType.CREW_BOOK_UNIVERSAL_BROCHURE)
    BLUEPRINTS = (ItemPackType.BLUEPRINT,
     ItemPackType.BLUEPRINT_ANY,
     ItemPackType.BLUEPRINT_NATIONAL,
     ItemPackType.BLUEPRINT_NATIONAL_ANY,
     ItemPackType.BLUEPRINT_INTELEGENCE_DATA)
    OFFER = (ItemPackType.OFFER_BATTLE_BOOSTER, ItemPackType.OFFER_BROCHURE)
    TMAN_TOKEN = {ItemPackType.TMAN_TOKEN}


CompensationSpec = namedtuple('CompensationSpec', ('type', 'value', 'count'))

def getItemPackByGroupAndName(group, name, default=None):
    return next((itemPackName for itemPackName in group if name in itemPackName), default)


class CompensationType(CONST_CONTAINER):
    MONEY = 'money'


def sanitizeResPath(relPath):
    if relPath:
        if relPath.startswith('img://'):
            relPath = relPath.replace('img://', '')
        if relPath.startswith('..'):
            relPath = 'gui' + relPath[2:]
        return relPath
