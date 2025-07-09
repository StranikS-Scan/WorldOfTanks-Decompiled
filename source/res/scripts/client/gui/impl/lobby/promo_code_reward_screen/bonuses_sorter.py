# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/promo_code_reward_screen/bonuses_sorter.py
import typing
from constants import LOOTBOX_TOKEN_PREFIX, PREMIUM_ENTITLEMENTS, LOOTBOX_KEY_PREFIX
from gui.impl.lobby.promo_code_reward_screen import isLootboxesExtensionAvailable
from gui.impl.lobby.promo_code_reward_screen.bonuses import QUESTS_BUNUS_NAME
from gui.server_events.bonuses import VehiclesBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IGuiLootBoxesController
VEHICLE_MAX_LEVEL = 10

class BonusesSortTags(object):
    UNSORTABLE = 'unsortable'
    VEHICLE = 'vehicle'
    UNIQUE_CUSTOMIZATION = 'uniqueCustomization'
    RARITY_OPT_DEV = 'rarityOptionalDevice'
    RARITY_CURRENCY = 'rarityCurrency'
    PREMIUM = 'premium'
    UNIQUE_TANKMEN = 'uniqueTankmen'
    TANKMEN = 'tankmen'
    STYLE = 'style'
    PERSONAL_BOOSTER = 'personalBooster'
    CREW_BOOK = 'crewBook'
    CURRENCY = 'ordinaryCurrency'
    OPT_DEV = 'optionalDevice'
    EQUIPMENT = 'equipment'
    BATTLE_BOOSTER = 'battleBooster'
    CUSTOMIZATION = 'customization'
    SLOT = 'slot'
    BERTH = 'berth'
    BLUEPRINT = 'blueprint'
    NARRATIVE_CLLC_ITEM = 'narrativeCollectionItem'
    CLLC_ITEM_COMP = 'collectionItemCompensation'
    CUSTOM_LOOTBOX = 'customLootBox'
    CUSTOM_LOOTBOXKEY = 'customLootBoxKey'
    RANGE = (UNSORTABLE,
     VEHICLE,
     UNIQUE_CUSTOMIZATION,
     RARITY_OPT_DEV,
     RARITY_CURRENCY,
     PREMIUM,
     UNIQUE_TANKMEN,
     TANKMEN,
     STYLE,
     PERSONAL_BOOSTER,
     CREW_BOOK,
     CURRENCY,
     OPT_DEV,
     EQUIPMENT,
     BATTLE_BOOSTER,
     CUSTOMIZATION,
     SLOT,
     BERTH,
     BLUEPRINT,
     NARRATIVE_CLLC_ITEM,
     CLLC_ITEM_COMP,
     CUSTOM_LOOTBOX,
     CUSTOM_LOOTBOXKEY)


_DEFAULT_ORDER = (BonusesSortTags.VEHICLE,
 QUESTS_BUNUS_NAME,
 BonusesSortTags.UNIQUE_CUSTOMIZATION,
 BonusesSortTags.RARITY_OPT_DEV,
 BonusesSortTags.RARITY_CURRENCY,
 BonusesSortTags.PREMIUM,
 BonusesSortTags.UNIQUE_TANKMEN,
 BonusesSortTags.TANKMEN,
 BonusesSortTags.STYLE,
 BonusesSortTags.PERSONAL_BOOSTER,
 BonusesSortTags.CREW_BOOK,
 BonusesSortTags.CURRENCY,
 BonusesSortTags.OPT_DEV,
 BonusesSortTags.EQUIPMENT,
 BonusesSortTags.BATTLE_BOOSTER,
 BonusesSortTags.CUSTOMIZATION,
 BonusesSortTags.SLOT,
 BonusesSortTags.BERTH,
 BonusesSortTags.BLUEPRINT,
 BonusesSortTags.NARRATIVE_CLLC_ITEM,
 BonusesSortTags.CLLC_ITEM_COMP,
 BonusesSortTags.UNSORTABLE)

def _getCustomizationTag(bonus):
    item = bonus.getC11nItem(first(bonus.getCustomizations()))
    if item.itemTypeID == GUI_ITEM_TYPE.STYLE and item.is3D:
        return BonusesSortTags.UNIQUE_CUSTOMIZATION
    return BonusesSortTags.STYLE if item.itemTypeID == GUI_ITEM_TYPE.STYLE else BonusesSortTags.CUSTOMIZATION


def _getGoodiesTag(bonus):
    booster = first(bonus.getBoosters().keys())
    if booster is not None:
        return BonusesSortTags.PERSONAL_BOOSTER
    else:
        rf = first(bonus.getRecertificationForms().keys())
        if rf is not None:
            return BonusesSortTags.CURRENCY
        dk = first(bonus.getDemountKits().keys())
        return BonusesSortTags.CURRENCY if dk is not None else BonusesSortTags.UNSORTABLE


def _getItemTag(bonus):
    item = first(bonus.getItems().keys())
    itemTypeID = item.itemTypeID
    if itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and (item.isDeluxe or item.isTrophy or item.isModernized):
        return BonusesSortTags.RARITY_OPT_DEV
    if itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        return BonusesSortTags.OPT_DEV
    return BonusesSortTags.EQUIPMENT if itemTypeID == GUI_ITEM_TYPE.EQUIPMENT else BonusesSortTags.BATTLE_BOOSTER


def _getTankmenTag(bonus):
    tankman = first(bonus.getTankmenDescriptors())
    return BonusesSortTags.UNIQUE_TANKMEN if tankman.isUnique else BonusesSortTags.TANKMEN


def _getTankmenTokenTag(bonus):
    info = getRecruitInfo(first(bonus.getTokens().iterkeys()))
    return BonusesSortTags.UNIQUE_TANKMEN if info and info.isUnique() else BonusesSortTags.TANKMEN


def _getTokensTag(bonus):
    tokenId = first(bonus.getTokens().iterkeys())
    if isLootboxesExtensionAvailable():
        from gui_lootboxes.gui.bonuses.bonuses_helpers import TOKEN_COMPENSATION_PREFIX, parseCompenstaionToken
        if tokenId.startswith(TOKEN_COMPENSATION_PREFIX):
            _, _, item, _ = parseCompenstaionToken(tokenId)
            if item == 'cllc':
                return BonusesSortTags.CLLC_ITEM_COMP
    if tokenId.startswith(LOOTBOX_TOKEN_PREFIX):
        return BonusesSortTags.CUSTOM_LOOTBOX
    return BonusesSortTags.CUSTOM_LOOTBOXKEY if tokenId.startswith(LOOTBOX_KEY_PREFIX) else BonusesSortTags.UNSORTABLE


BONUS_TAG_HANDLER_MAP = {Currency.CREDITS: lambda b: BonusesSortTags.CURRENCY,
 Currency.GOLD: lambda b: BonusesSortTags.RARITY_CURRENCY,
 Currency.CRYSTAL: lambda b: BonusesSortTags.RARITY_CURRENCY,
 Currency.EVENT_COIN: lambda b: BonusesSortTags.CURRENCY,
 Currency.BPCOIN: lambda b: BonusesSortTags.CURRENCY,
 Currency.EQUIP_COIN: lambda b: BonusesSortTags.RARITY_CURRENCY,
 'slots': lambda b: BonusesSortTags.SLOT,
 'berths': lambda b: BonusesSortTags.BERTH,
 PREMIUM_ENTITLEMENTS.BASIC: lambda b: BonusesSortTags.PREMIUM,
 PREMIUM_ENTITLEMENTS.PLUS: lambda b: BonusesSortTags.PREMIUM,
 VehiclesBonus.VEHICLES_BONUS: lambda b: BonusesSortTags.VEHICLE,
 'tankmen': _getTankmenTag,
 'customizations': _getCustomizationTag,
 'goodies': _getGoodiesTag,
 'items': _getItemTag,
 'blueprints': lambda b: BonusesSortTags.BLUEPRINT,
 'blueprintsAny': lambda b: BonusesSortTags.BLUEPRINT,
 'crewSkins': lambda b: BonusesSortTags.CUSTOMIZATION,
 'collectionItem': lambda b: BonusesSortTags.NARRATIVE_CLLC_ITEM,
 'randomCrewbook': lambda b: BonusesSortTags.CREW_BOOK,
 'crewBooks': lambda b: BonusesSortTags.CREW_BOOK,
 'dogTagComponents': lambda b: BonusesSortTags.CUSTOMIZATION,
 'dossier': lambda b: BonusesSortTags.CUSTOMIZATION,
 'tmanToken': _getTankmenTokenTag,
 'battleToken': _getTokensTag,
 'freeXP': lambda b: BonusesSortTags.CURRENCY,
 QUESTS_BUNUS_NAME: lambda b: QUESTS_BUNUS_NAME}

def getVehBonusSortKey(bonus):
    vehicle, _ = first(bonus.getVehicles())
    return (-vehicle.level,
     bool(vehicle.isRented),
     not vehicle.isPremium,
     not vehicle.isSpecial,
     not vehicle.isUnique,
     vehicle)


@dependency.replace_none_kwargs(guiLootBoxController=IGuiLootBoxesController)
def getTokensSortKey(bonus, guiLootBoxController=None):
    tokenId = first(bonus.getTokens().iterkeys())
    if tokenId.startswith(LOOTBOX_KEY_PREFIX) and guiLootBoxController is not None:
        lbKey = guiLootBoxController.getKeyByTokenID(tokenId)
        if lbKey is not None:
            return -lbKey.openProbability
    if tokenId.startswith(LOOTBOX_TOKEN_PREFIX) and guiLootBoxController is not None:
        lb = guiLootBoxController.getGuiLootBoxByTokenID(tokenId)
        if lb is not None:
            return -lb.getWeight()
    return bonus.getName()


BONUSES_KEY_FUNC = {'items': lambda b: first(b.getItems()),
 'crewBooks': lambda b: first(b.getItems()),
 'vehicles': getVehBonusSortKey,
 'battleToken': getTokensSortKey}

def _defaultBonusKeyFunc(bonus):
    return bonus.getName()


def getBonusSortTag(bonus):
    return BONUS_TAG_HANDLER_MAP.get(bonus.getName(), lambda b: BonusesSortTags.UNSORTABLE)(bonus)


def getBonusesSortKeyFunc(order):
    return lambda b: (order.index(getBonusSortTag(b)), BONUSES_KEY_FUNC.get(b.getName(), _defaultBonusKeyFunc)(b))


def sortBonuses(bonuses, order=None):
    order = order or _DEFAULT_ORDER
    return sorted(bonuses, key=getBonusesSortKeyFunc(order))
