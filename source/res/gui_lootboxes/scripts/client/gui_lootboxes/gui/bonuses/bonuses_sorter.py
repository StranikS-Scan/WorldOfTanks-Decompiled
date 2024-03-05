# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/bonuses/bonuses_sorter.py
import typing
from constants import LOOTBOX_TOKEN_PREFIX, PREMIUM_ENTITLEMENTS
from gui.server_events.bonuses import VehiclesBonus, splitBonuses
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from gui_lootboxes.gui.bonuses.bonuses_helpers import TOKEN_COMPENSATION_PREFIX, parseCompenstaionToken
from gui_lootboxes.gui.bonuses.bonuses_order_config import BonusesSortTags
from shared_utils import first
VEHICLE_MAX_LEVEL = 10

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
    if tokenId.startswith(TOKEN_COMPENSATION_PREFIX):
        _, _, item, _ = parseCompenstaionToken(tokenId)
        if item == 'cllc':
            return BonusesSortTags.CLLC_ITEM_COMP
    return BonusesSortTags.CUSTOM_LOOTBOX if tokenId.startswith(LOOTBOX_TOKEN_PREFIX) else BonusesSortTags.UNSORTABLE


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
 'freeXP': lambda b: BonusesSortTags.CURRENCY}

def getVehBonusSortKey(bonus):
    vehicle, vehInfo = first(bonus.getVehicles())
    compensatedNumber = vehInfo.get('compensatedNumber', 0)
    compensation = vehInfo.get('customCompensation')
    hasCompensation = compensatedNumber and compensation is not None
    return (hasCompensation, -vehicle.level, vehicle)


BONUSES_KEY_FUNC = {'items': lambda b: first(b.getItems()),
 'crewBooks': lambda b: first(b.getItems()),
 'vehicles': getVehBonusSortKey}

def _defaultBonusKeyFunc(bonus):
    return bonus.getName()


def getBonusSortTag(bonus):
    return BONUS_TAG_HANDLER_MAP.get(bonus.getName(), lambda b: BonusesSortTags.UNSORTABLE)(bonus)


def getBonusesSortKeyFunc(order):
    return lambda b: (order.index(getBonusSortTag(b)), BONUSES_KEY_FUNC.get(b.getName(), _defaultBonusKeyFunc)(b))


def sortBonuses(bonuses, order):
    return sorted(splitBonuses(bonuses), key=getBonusesSortKeyFunc(order))
