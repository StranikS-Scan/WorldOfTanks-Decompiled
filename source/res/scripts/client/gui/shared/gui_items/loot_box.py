# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/loot_box.py
import typing
import logging
from enum import Enum
from constants import LootBoxTiers, LOOTBOX_LIMIT_ITEM_PREFIX
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.loot_box_bonus_group import LootBoxBonusGroup as BonusGroup
from gui.impl.lobby.loot_box.loot_box_helper import parseAllOfBonusInfoSection
from gui.shared.gui_items.gui_item import GUIItem
from shared_utils import CONST_CONTAINER
from web.web_client_api.common import ItemPackType as ipType, ItemPackTypeGroup as ipTypeGroup
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, Optional
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)

class NewYearLootBoxes(CONST_CONTAINER):
    PREMIUM = 'newYear_premium'
    SPECIAL = 'newYear_special'
    SPECIAL_AUTO = 'newYear_special_auto'
    COMMON = 'newYear_usual'


class NewYearCategories(CONST_CONTAINER):
    NEWYEAR = 'NewYear'
    CHRISTMAS = 'Christmas'
    ORIENTAL = 'Oriental'
    FAIRYTALE = 'Fairytale'


class EventCategories(CONST_CONTAINER):
    EVENT = 'Event'


class WTLootBoxes(CONST_CONTAINER):
    WT_HUNTER = 'wt_hunter'
    WT_BOSS = 'wt_boss'
    WT_SPECIAL = 'wt_special'


class LunarNYLootBoxTypes(Enum):
    BASE = 'lunar_base'
    SIMPLE = 'lunar_simple'
    SPECIAL = 'lunar_special'


class EventLootBoxes(CONST_CONTAINER):
    PREMIUM = 'event_premium'
    COMMON = 'event_common'


class ReferralProgramLootBoxes(CONST_CONTAINER):
    SMALL = 'small_referral'
    BIG = 'big_referral'
    SPECIAL = 'special_referral'


ALL_LUNAR_NY_LOOT_BOX_TYPES = ('lunar_base', 'lunar_simple', 'lunar_special')
LUNAR_NY_LOOT_BOXES_CATEGORIES = 'LunarNY'
SENIORITY_AWARDS_LOOT_BOXES_TYPE = 'seniorityAwards'
EVENT_LOOT_BOXES_CATEGORY = 'eventLootBoxes'
REFERRAL_PROGRAM_CATEGORY = 'referralProgram'
GUI_ORDER_NY = (NewYearLootBoxes.COMMON, NewYearLootBoxes.PREMIUM)
CATEGORIES_GUI_ORDER_NY = (NewYearCategories.NEWYEAR,
 NewYearCategories.CHRISTMAS,
 NewYearCategories.ORIENTAL,
 NewYearCategories.FAIRYTALE)
_BONUS_GROUPS = {BonusGroup.VEHICLE: ipTypeGroup.VEHICLE,
 BonusGroup.PREMIUM: (ipType.CUSTOM_PREMIUM_PLUS,),
 BonusGroup.CURRENCY: (ipType.CUSTOM_CREDITS,
                       ipType.CUSTOM_GOLD,
                       ipType.CUSTOM_FREE_XP,
                       ipType.CUSTOM_CRYSTAL),
 BonusGroup.VEHICLECUSTOMIZATIONS: ipTypeGroup.CUSTOMIZATION,
 BonusGroup.CREW: ipTypeGroup.CREW + ipTypeGroup.CREW_BOOKS + tuple(ipTypeGroup.TMAN_TOKEN) + (ipType.GOODIE_RECERTIFICATIONFORM, ipType.ITEM_CREW_SKIN),
 BonusGroup.BOOSTERS: ipTypeGroup.GOODIE + (ipType.CUSTOM_X5_BATTLE_BONUS,) + ipTypeGroup.BLUEPRINTS,
 BonusGroup.EQUIPMENTS: ipTypeGroup.ITEM + (ipType.DEMOUNT_KITS, ipType.CUSTOM_SEVERAL_SLOTS),
 BonusGroup.ACCOUNTCUSTOMIZATIONS: (ipType.ACHIEVEMENT,
                                    ipType.BADGE,
                                    ipType.SINGLE_ACHIEVEMENTS,
                                    ipType.PLAYER_BADGE,
                                    ipType.CUSTOM_DOG_TAG),
 BonusGroup.FEATUREITEMS: (ipType.CUSTOM_COLLECTION_ENTITLEMENT, ipType.CUSTOM_ANY_COLLECTION_ITEM)}
_GROUP_PRIORITIES = [BonusGroup.VEHICLE,
 BonusGroup.PREMIUM,
 BonusGroup.CURRENCY,
 BonusGroup.VEHICLECUSTOMIZATIONS,
 BonusGroup.CREW,
 BonusGroup.BOOSTERS,
 BonusGroup.EQUIPMENTS,
 BonusGroup.ACCOUNTCUSTOMIZATIONS,
 BonusGroup.FEATUREITEMS]

def addBonusesToGroup(bonusGroup, bonuses):
    _BONUS_GROUPS[bonusGroup] += bonuses


class LootBox(GUIItem):
    __slots__ = ('__id', '__invCount', '__type', '__category', '__historyName', '__guaranteedFrequency', '__slotBonuses', '__guaranteedFrequencyName', '__tier', '__isEnabled', '__userNameKey', '__iconName', '__description', '__videoKey', '__weight', '__bonusGroups')

    def __init__(self, lootBoxID, lootBoxConfig, invCount):
        super(LootBox, self).__init__()
        self.__id = lootBoxID
        self.__invCount = invCount
        self.__updateByConfig(lootBoxConfig)

    def __repr__(self):
        return 'LootBox(lootBoxID={}, lootBoxConfig={}, invCount={})'.format(self.getID(), self.__getConfig(), self.getInventoryCount())

    def __cmp__(self, other):
        return cmp(-self.getWeight(), -other.getWeight())

    def updateCount(self, invCount):
        self.__invCount = invCount

    def update(self, lootBoxConfig):
        self.__updateByConfig(lootBoxConfig)

    def getInventoryCount(self):
        return self.__invCount

    def getID(self):
        return self.__id

    def getUserName(self):
        return backport.text(R.strings.lootboxes.userName.dyn(self.__userNameKey)())

    def getUserNameKey(self):
        return self.__userNameKey

    def getDesrciption(self):
        return self.__description

    def getIconName(self):
        return self.__iconName

    def getVideoRes(self):
        resource = R.videos
        resPath = self.__videoKey.split('/')
        if resPath:
            for pathItem in resPath:
                resource = resource.dyn(pathItem)
                if not resource:
                    return R.invalid()

            return resource()
        return R.invalid()

    def getType(self):
        return self.__type

    def getCategory(self):
        return self.__category

    def getTier(self):
        return self.__tier

    def getWeight(self):
        return self.__weight

    def isFree(self):
        return self.__type == NewYearLootBoxes.COMMON

    def isEnabled(self):
        return self.__isEnabled

    def getGuaranteedFrequency(self):
        return self.__guaranteedFrequency

    def getGuaranteedFrequencyName(self):
        return self.__guaranteedFrequencyName

    def getHistoryName(self):
        return self.__historyName

    def getBonusGroups(self):
        if self.__bonusGroups is None:
            self.__bonusGroups = self.__formBonusGroups(self.__slotBonuses)
        return sorted(self.__bonusGroups.keys(), key=_GROUP_PRIORITIES.index)

    def getBonusesByGroup(self, group):
        return self.__bonusGroups[group]

    def getBonusSlots(self):
        return self.__slotBonuses

    def getBoxInfo(self, historyData=None):
        return {'id': self.getID(),
         'limit': self.getGuaranteedFrequency(),
         'slots': self.__slotBonuses,
         'history': historyData.get(self.getHistoryName(), (0, None, 0)) if historyData is not None else (0, None, 0)}

    def __updateByConfig(self, lootBoxConfig):
        self.__type = lootBoxConfig.get('type', '')
        self.__category = lootBoxConfig.get('category', '')
        self.__tier = LootBoxTiers(lootBoxConfig.get('tier', 1))
        self.__historyName = lootBoxConfig.get('historyName', '')
        self.__slotBonuses = parseAllOfBonusInfoSection(lootBoxConfig.get('bonus', {}).get('allof', {}))
        self.__bonusGroups = None
        self.__guaranteedFrequencyName, self.__guaranteedFrequency = self.__readLimits(lootBoxConfig.get('limits', {}))
        self.__isEnabled = lootBoxConfig.get('enabled', False)
        self.__weight = lootBoxConfig.get('weight', 0.0)
        assetsConfig = lootBoxConfig.get('assets', {})
        self.__userNameKey = assetsConfig.get('userName', self.__type)
        iconName = assetsConfig.get('iconName', self.__type)
        self.__iconName = iconName if iconName else 'default'
        self.__description = assetsConfig.get('description', self.__type)
        self.__videoKey = assetsConfig.get('video', '')
        return

    def __getConfig(self):
        return {'type': self.__type,
         'category': self.__category,
         'tier': self.__tier,
         'enabled': self.__isEnabled,
         'weight': self.__weight,
         'assets': {'userName': self.__userNameKey,
                    'iconName': self.__iconName,
                    'description': self.__description,
                    'video': self.__videoKey}}

    @staticmethod
    def __readLimits(limitsCfg):
        for limitName, limit in limitsCfg.iteritems():
            if 'useBonusProbabilityAfter' in limit:
                return (limitName, limit['useBonusProbabilityAfter'] + 1)

        return (None, 0)

    def __formBonusGroups(self, slots):
        bonusGroups = dict()
        for _, slot in slots.items():
            for bonus in slot.get('bonuses', {}):
                bonusGroup = self.__findGroupForBonus(bonus)
                if bonusGroup is None:
                    if not self.__isExcludedBonus(bonus):
                        _logger.warning('Could not find a proper BonusGroup for bonus: %s', bonus.getName())
                    continue
                bonusGroups.setdefault(bonusGroup, []).append(bonus)

        return bonusGroups

    @staticmethod
    def __findGroupForBonus(bonus):
        for bns in bonus.getWrappedLootBoxesBonusList():
            bonusType = bns['type']
            for bonusGroup, bonusTypes in _BONUS_GROUPS.items():
                if bonusType in bonusTypes:
                    return bonusGroup

        return None

    def __isExcludedBonus(self, bonus):
        value = bonus.getValue()
        if isinstance(value, dict):
            for k in value.keys():
                if LOOTBOX_LIMIT_ITEM_PREFIX in str(k):
                    return True

        return False
