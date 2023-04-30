# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/bonuses_sorter.py
from enum import IntEnum
import constants
from gui.goodies.goodie_items import BOOSTERS_ORDERS
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from items.components.supply_slot_categories import SlotCategories
from shared_utils import first

class BonusesSortWeights(IntEnum):
    UNSORTABLE = 0
    DEMOUNT_KIT = 1
    BOOSTER_GOODIE = 2
    BATTLE_BOOSTER = 3
    CREDITS = 4
    FREE_XP = 5
    CRYSTALS = 6
    RECERTIFICATION_FORM = 7
    SLOTS = 8
    PREMUIM_PLUS = 9
    OPTIONAL_DEVICE = 10
    VEHICLE = 11


def _itemsBonusKeyFunc(bonus):
    item = first(bonus.getItems().keys())
    itemTypeID = item.itemTypeID
    if itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
        return (-BonusesSortWeights.BATTLE_BOOSTER, item)
    if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        return (-BonusesSortWeights.OPTIONAL_DEVICE, (not item.isDeluxe,
          [ category not in item.descriptor.categories for category in SlotCategories.ORDER ],
          item.getBuyPrice().price,
          item.userName))
    return (BonusesSortWeights.UNSORTABLE, bonus.getName())


def _goodieBonusKeyFunc(bonus):
    booster = first(bonus.getBoosters().keys())
    if booster is not None:
        return (-BonusesSortWeights.BOOSTER_GOODIE, (-BOOSTERS_ORDERS.get(booster.boosterType, 0), not booster.getIsPremium()))
    else:
        demountKit = first(bonus.getDemountKits().keys())
        if demountKit is not None:
            return (-BonusesSortWeights.DEMOUNT_KIT, 0)
        recertificationForms = first(bonus.getRecertificationForms().keys())
        return (-BonusesSortWeights.RECERTIFICATION_FORM, 0) if recertificationForms is not None else (BonusesSortWeights.UNSORTABLE, bonus.getName())


def _vehiclesBonusKeyFunc(bonus):
    vehicle = first(bonus.getVehicles())
    return (-BonusesSortWeights.VEHICLE, -vehicle[0].level) if vehicle is not None else (-BonusesSortWeights.VEHICLE, 0)


_BONUSES_KEYS_FUNC = {VehiclesBonus.VEHICLES_BONUS: _vehiclesBonusKeyFunc,
 'items': _itemsBonusKeyFunc,
 constants.PREMIUM_ENTITLEMENTS.PLUS: lambda b: (-BonusesSortWeights.PREMUIM_PLUS, 0),
 'slots': lambda b: (-BonusesSortWeights.SLOTS, 0),
 Currency.CREDITS: lambda b: (-BonusesSortWeights.CREDITS, 0),
 Currency.CRYSTAL: lambda b: (-BonusesSortWeights.CRYSTALS, 0),
 'freeXP': lambda b: (-BonusesSortWeights.FREE_XP, 0),
 'goodies': _goodieBonusKeyFunc}

def bonusesSortKeyFunc(bonus):
    return _BONUSES_KEYS_FUNC.get(bonus.getName(), lambda b: (BonusesSortWeights.UNSORTABLE, bonus.getName()))(bonus)
