# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/bonuses_layout_helpers.py
from __future__ import absolute_import
import logging
from enum import Enum
from typing import TYPE_CHECKING
from gui.server_events.bonuses import IntelligenceBlueprintBonus, NationalBlueprintBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.blueprints_requester import getVehicleCDForIntelligence, getVehicleCDForNational
from shared_utils import first
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union
    from gui.server_events.bonuses import CustomizationsBonus, GoodiesBonus, ItemsBonus, LootBoxTokensBonus, SimpleBonus, TmanTemplateTokensBonus, TokensBonus, VehicleBlueprintBonus, VehiclesBonus

class BonusesLayoutAttrs(object):
    BONUSES = 'bonuses'
    DEFAULT = 'default'
    PRIORITY = 'priority'
    VISIBILITY = 'isVisible'
    OVERRIDE = 'override'
    RARITY = 'rarity'
    ID = 'id'
    MAIN = (PRIORITY, VISIBILITY)


class _HelperTypes(str, Enum):
    RENT = 'rent'
    LOCKED_STYLE = 'lockedStyle'
    STYLE_3D = 'style3D'
    TROPHY_DEVICE = 'trophyDevice'
    MODERNIZED_DEVICE = 'modernizedDevice'
    IMPROVED_DEVICE = 'improvedDevice'
    OPTIONAL_DEVICE = 'optionalDevice'
    CREW_BATTLE_BOOSTER = 'crewBattleBooster'
    DEVICE_BATTLE_BOOSTER = 'deviceBattleBooster'
    CONSUMABLE = 'consumable'
    STIMULATOR = 'stimulator'
    DEMOUNT_KIT = 'demountKit'
    RECERTIFICATION_FORM = 'recertificationForm'
    MENTORING_LICENSE = 'mentoringLicense'
    TANKWOMAN = 'tankwoman'


class BonusesLayoutHelper(object):

    @classmethod
    def getParameter(cls, bonus, source, parameter, subTypeGetter=None, valueGetter=None):
        default = source.get(parameter)
        subType = cls.__getSubType(bonus, subTypeGetter)
        source = source.get(subType, source)
        default = source.get(parameter, default)
        value = cls.__getValue(bonus, source, valueGetter)
        source = source.get(value, source)
        default = source.get(parameter, default)
        return source.get(parameter, default)

    @classmethod
    def __getSubType(cls, bonus, subTypeGetter):
        getter = subTypeGetter() if subTypeGetter is not None else getDefaultSubTypeGetter()
        return cls.__selectGetter(bonus, getter, BaseSubTypeGetter).getSubType(bonus)

    @classmethod
    def __getValue(cls, bonus, source, valueGetter):
        getter = valueGetter() if valueGetter is not None else getDefaultValueGetter()
        return cls.__selectGetter(bonus, getter, BaseValueGetter).getValue(bonus, source)

    @staticmethod
    def __selectGetter(bonus, getters, default):
        return getters.get(bonus.getName(), default)


class BaseSubTypeGetter(object):

    @staticmethod
    def getSubType(bonus):
        _logger.debug('No subType getter for bonus: %s', bonus.getName())
        return None


class VehiclesSubTypeGetter(BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        subType = ''
        vehicles = bonus.getVehicles()
        vehicle, vehInfo = first(vehicles)
        if vehicle.isOutfitLocked:
            subType = _HelperTypes.LOCKED_STYLE
        if bonus.isRentVehicle(vehInfo):
            subType = _HelperTypes.RENT
        return subType


class CustomizationSubTypeGetter(BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        customizations = bonus.getCustomizations()
        itemData = first(customizations)
        c11nItem = bonus.getC11nItem(itemData)
        itemType = c11nItem.itemTypeName
        if itemType == 'style':
            if c11nItem.isLockedOnVehicle:
                return _HelperTypes.LOCKED_STYLE
            if c11nItem.is3D:
                return _HelperTypes.STYLE_3D
        return itemType


class GoodiesSubTypeGetter(BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        subType = ''
        if bonus.getDemountKits():
            return _HelperTypes.DEMOUNT_KIT
        if bonus.getRecertificationForms():
            return _HelperTypes.RECERTIFICATION_FORM
        return _HelperTypes.MENTORING_LICENSE if bonus.getMentoringLicenses() else subType


class ItemsSubTypeGetter(BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        subType = ''
        items = bonus.getItems()
        item = first(items)
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            if item.isTrophy:
                subType = _HelperTypes.TROPHY_DEVICE
            elif item.isModernized:
                subType = _HelperTypes.MODERNIZED_DEVICE
            elif item.isDeluxe:
                subType = _HelperTypes.IMPROVED_DEVICE
            else:
                subType = _HelperTypes.OPTIONAL_DEVICE
        elif item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            subType = _HelperTypes.CONSUMABLE
            if item.isStimulator:
                subType = _HelperTypes.STIMULATOR
        elif item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            if item.isCrewBooster():
                subType = _HelperTypes.CREW_BATTLE_BOOSTER
            else:
                subType = _HelperTypes.DEVICE_BATTLE_BOOSTER
        return subType


class TankmanSubTypeGetter(BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        keys = bonus.getValue()
        tID = first(keys)
        recruitInfo = getRecruitInfo(tID)
        return _HelperTypes.TANKWOMAN if recruitInfo.isFemale() else ''


class CurrenciesSubTypeGetter(BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        return bonus.getCode()


class BaseValueGetter(object):

    @classmethod
    def getValue(cls, bonus, _):
        _logger.debug('No value getter for bonus: %s', bonus.getName())
        return None


class IntCDValueGetter(BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        keys = bonus.getValue()
        value = str(first(keys))
        return value


class BlueprintValueGetter(BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, source):
        intCD = first(bonus.getValue())
        if isinstance(bonus, (IntelligenceBlueprintBonus, NationalBlueprintBonus)):
            for key in source.keys():
                if key not in BonusesLayoutAttrs.MAIN:
                    if intCD == cls.__transformKey(key, bonus):
                        return key

        return str(intCD)

    @staticmethod
    def __transformKey(key, bonus):
        intCD = int(key)
        if isinstance(bonus, IntelligenceBlueprintBonus):
            intCD = getVehicleCDForIntelligence(intCD)
        elif isinstance(bonus, NationalBlueprintBonus):
            intCD = getVehicleCDForNational(intCD)
        return intCD


class CustomizationValueGetter(BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        customizations = bonus.getCustomizations()
        itemData = first(customizations)
        if itemData.get('custType', '') == 'attachment':
            c11nItem = bonus.getC11nItem(itemData)
            return c11nItem.rarity
        return str(itemData.get('id', ''))


class VehiclesValueGetter(BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        value = bonus.getValue()
        if isinstance(value, list):
            value = first(value)
        return str(first(value.keys()))


class TankmanValueGetter(BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        keys = bonus.getValue()
        tID = first(keys)
        recruitInfo = getRecruitInfo(tID)
        return recruitInfo.getGroupName()


class TokenValueGetter(BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        return first(bonus.getTokens(), '')


class LootBoxValueGetter(BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        box = bonus.getBox()
        return '{}_{}'.format(box.getType(), box.getCategory())


def getDefaultValueGetter():
    return {'default': BaseValueGetter,
     'blueprints': BlueprintValueGetter,
     'items': IntCDValueGetter,
     'goodies': IntCDValueGetter,
     'crewBooks': IntCDValueGetter,
     'customizations': CustomizationValueGetter,
     'vehicles': VehiclesValueGetter,
     'tmanToken': TankmanValueGetter,
     'tokens': TokenValueGetter,
     'lootBox': LootBoxValueGetter}


def getDefaultSubTypeGetter():
    return {'default': BaseSubTypeGetter,
     'customizations': CustomizationSubTypeGetter,
     'currencies': CurrenciesSubTypeGetter,
     'goodies': GoodiesSubTypeGetter,
     'items': ItemsSubTypeGetter,
     'vehicles': VehiclesSubTypeGetter,
     'tmanToken': TankmanSubTypeGetter}
