# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/bonuses_sorter.py
from enum import IntEnum
import constants
from gui.goodies.goodie_items import BOOSTERS_ORDERS
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from items.components.supply_slot_categories import SlotCategories
from shared_utils import first

class BonusesSortWeights(IntEnum):
    DEMOUNT_KIT = 0
    UNSORTABLE = 1
    SLOTS = 2
    BOOSTER_GOODIE = 3
    CREW_BATTLE_BOOSTER = 4
    BATTLE_BOOSTER = 5
    RECERTIFICATION_FORM = 6
    CREDITS = 7
    BOOSTER_CREDITS = 8
    CREW_BOOK = 9
    TMAN = 10
    FREE_XP = 11
    GOLD = 12
    CRYSTALS = 13
    PREMUIM_PLUS = 14
    STYLE = 15
    OPTIONAL_DEVICE = 16
    LOOTBOX = 17
    VEHICLE = 18


def itemsBonusKeyFunc(bonus):
    item = first(bonus.getItems().keys())
    if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
        if 'crewSkillBattleBooster' in item.tags:
            return (-BonusesSortWeights.CREW_BATTLE_BOOSTER, item.shortUserName)
        return (-BonusesSortWeights.BATTLE_BOOSTER, item.shortUserName)
    if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        return (-BonusesSortWeights.OPTIONAL_DEVICE, (not item.isDeluxe,
          [ category not in item.descriptor.categories for category in SlotCategories.ORDER ],
          item.getBuyPrice().price,
          item.userName))
    return (BonusesSortWeights.UNSORTABLE, bonus.getName())


def goodieBonusKeyFunc(bonus):
    booster = first(bonus.getBoosters().keys())
    if booster is not None:
        if booster.boosterGuiType == 'booster_credits':
            return (-BonusesSortWeights.BOOSTER_CREDITS, 0)
        return (-BonusesSortWeights.BOOSTER_GOODIE, (-BOOSTERS_ORDERS.get(booster.boosterType, 0), not booster.getIsPremium()))
    else:
        demountKit = first(bonus.getDemountKits().keys())
        if demountKit is not None:
            return (-BonusesSortWeights.DEMOUNT_KIT, 0)
        recertificationForms = first(bonus.getRecertificationForms().keys())
        return (-BonusesSortWeights.RECERTIFICATION_FORM, 0) if recertificationForms is not None else (BonusesSortWeights.UNSORTABLE, bonus.getName())


def vehiclesBonusKeyFunc(bonus):
    vehicle = first(bonus.getVehicles())
    return (-BonusesSortWeights.VEHICLE, -vehicle[0].level) if vehicle is not None else (-BonusesSortWeights.VEHICLE, 0)


def tokensBonusKeyFunc(bonus):
    tokenId = first(bonus.getTokens().iterkeys())
    return (-BonusesSortWeights.LOOTBOX, 0) if tokenId.startswith(constants.LOOTBOX_TOKEN_PREFIX) else (BonusesSortWeights.UNSORTABLE, 0)


_BONUSES_KEYS_FUNC = {VehiclesBonus.VEHICLES_BONUS: vehiclesBonusKeyFunc,
 'items': itemsBonusKeyFunc,
 constants.PREMIUM_ENTITLEMENTS.PLUS: lambda b: (-BonusesSortWeights.PREMUIM_PLUS, 0),
 'slots': lambda b: (-BonusesSortWeights.SLOTS, 0),
 Currency.CREDITS: lambda b: (-BonusesSortWeights.CREDITS, 0),
 Currency.GOLD: lambda b: (-BonusesSortWeights.GOLD, 0),
 Currency.CRYSTAL: lambda b: (-BonusesSortWeights.CRYSTALS, 0),
 'freeXP': lambda b: (-BonusesSortWeights.FREE_XP, 0),
 'goodies': goodieBonusKeyFunc,
 'tmanToken': lambda b: (-BonusesSortWeights.TMAN, 0),
 'crewBooks': lambda b: (-BonusesSortWeights.CREW_BOOK, 0),
 'customizations': lambda b: (-BonusesSortWeights.STYLE, 0),
 'battleToken': tokensBonusKeyFunc}

def _getBonusesKeysFuncMapping(extraKeysFuncs=None):
    keysFuncs = _BONUSES_KEYS_FUNC.copy()
    if extraKeysFuncs is not None:
        keysFuncs.update(extraKeysFuncs)
    return keysFuncs


def getBonusesSortKeyFunc(extraKeysFuncs=None):
    keysFuncs = _getBonusesKeysFuncMapping(extraKeysFuncs)

    def sortKeyFunc(bonus):
        return keysFuncs.get(bonus.getName(), lambda b: (BonusesSortWeights.UNSORTABLE, bonus.getName()))(bonus)

    return sortKeyFunc


def bonusesSortKeyFunc(bonus):
    return _BONUSES_KEYS_FUNC.get(bonus.getName(), lambda b: (BonusesSortWeights.UNSORTABLE, bonus.getName()))(bonus)
