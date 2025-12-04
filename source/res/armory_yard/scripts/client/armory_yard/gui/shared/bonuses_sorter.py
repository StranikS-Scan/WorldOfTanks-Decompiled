# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/bonuses_sorter.py
import typing
from enum import IntEnum
import constants
from gui.goodies.goodie_items import BOOSTERS_ORDERS
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from items.components.c11n_components import VehicleFilter
from items.components.supply_slot_categories import SlotCategories
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.shared.missions.packers.bonus import ItemsBonus, GoodiesBonus, SimpleBonus

class BonusesSortWeights(IntEnum):
    UNSORTABLE = 0
    SLOTS = 1
    CUSTOMIZATION = 2
    BOOSTER_GOODIE = 3
    CREW_BATTLE_BOOSTER = 4
    BATTLE_BOOSTER = 5
    AY_COIN = 6
    CREDITS = 7
    FREE_XP = 8
    DEMOUNT_KIT = 9
    RECERTIFICATION_FORM = 10
    CREW_BOOK = 11
    BOOSTER_CREDITS = 12
    STYLE = 13
    TMAN = 14
    PREMUIM_PLUS = 15
    CRYSTALS = 16
    EQUIP_COIN = 17
    OPTIONAL_DEVICE = 18
    LOOTBOX = 19
    UNIQUE_CUSTOMIZATION = 20
    VEHICLE = 21


def _itemsBonusKeyFunc(bonus):
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


def _goodieBonusKeyFunc(bonus):
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


def _vehiclesBonusKeyFunc(bonus):
    vehicle = first(bonus.getVehicles())
    return (-BonusesSortWeights.VEHICLE, -vehicle[0].level) if vehicle is not None else (-BonusesSortWeights.VEHICLE, 0)


def _customizationsBonusKeyFunc(bonus):
    item = bonus.getC11nItem(first(bonus.getCustomizations()))
    if item.itemTypeID == GUI_ITEM_TYPE.STYLE:
        itemFilter = item.descriptor.filter
        vehiclesForStyle = []
        if isinstance(itemFilter, VehicleFilter):
            for node in itemFilter.include:
                if node.vehicles:
                    vehiclesForStyle.extend(node.vehicles)

        if len(vehiclesForStyle) == 1:
            return (-BonusesSortWeights.UNIQUE_CUSTOMIZATION, 0)
        return (-BonusesSortWeights.STYLE, 0)
    return (-BonusesSortWeights.CUSTOMIZATION, 0)


_BONUSES_KEYS_FUNC = {VehiclesBonus.VEHICLES_BONUS: _vehiclesBonusKeyFunc,
 'items': _itemsBonusKeyFunc,
 constants.PREMIUM_ENTITLEMENTS.PLUS: lambda b: (-BonusesSortWeights.PREMUIM_PLUS, 0),
 'slots': lambda b: (-BonusesSortWeights.SLOTS, 0),
 Currency.CREDITS: lambda b: (-BonusesSortWeights.CREDITS, 0),
 Currency.CRYSTAL: lambda b: (-BonusesSortWeights.CRYSTALS, 0),
 Currency.EQUIP_COIN: lambda b: (-BonusesSortWeights.EQUIP_COIN, 0),
 Currency.AYCOIN: lambda b: (-BonusesSortWeights.AY_COIN, 0),
 'freeXP': lambda b: (-BonusesSortWeights.FREE_XP, 0),
 'goodies': _goodieBonusKeyFunc,
 'tmanToken': lambda b: (-BonusesSortWeights.TMAN, 0),
 'crewBooks': lambda b: (-BonusesSortWeights.CREW_BOOK, 0),
 'customizations': _customizationsBonusKeyFunc,
 'lootBoxToken': lambda b: (-BonusesSortWeights.LOOTBOX, 0)}

def bonusesSortKeyFunc(bonus):
    return _BONUSES_KEYS_FUNC.get(bonus.getName(), lambda b: (BonusesSortWeights.UNSORTABLE, bonus.getName()))(bonus)
