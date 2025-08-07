# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/bonuses_helper.py
import logging
import typing
from gui.impl.lobby.wot_anniversary.bonuses_constants import BonusesLayoutConsts
from gui.server_events.bonuses import IntelligenceBlueprintBonus, NationalBlueprintBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.blueprints_requester import getVehicleCDForIntelligence, getVehicleCDForNational
from shared_utils import first
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from gui.server_events.bonuses import SimpleBonus, VehicleBlueprintBonus, ItemsBonus, CurrenciesBonus, CustomizationsBonus, TokensBonus
_logger = logging.getLogger(__name__)

class BonusesHelper(object):

    @classmethod
    def getParameter(cls, bonus, source, parameter):
        result = source
        defaultValue = result.get(parameter)
        subType = cls.__getSubType(bonus)
        if subType in result:
            result = result[subType]
            defaultValue = result.get(parameter, defaultValue)
        value = cls.__getValue(bonus, result)
        if value in result:
            result = result.get(value, {})
            defaultValue = result.get(parameter, defaultValue)
        return result.get(parameter, defaultValue)

    @classmethod
    def __getSubType(cls, bonus):
        getter = cls.__selectGetter(bonus, _SUB_TYPE_GETTERS_MAP)
        return None if getter is None else getter.getSubType(bonus)

    @classmethod
    def __getValue(cls, bonus, source):
        getter = cls.__selectGetter(bonus, _VALUE_GETTERS_MAP)
        return None if getter is None else getter.getValue(bonus, source)

    @staticmethod
    def __selectGetter(bonus, getters):
        return getters.get(bonus.getName(), getters.get('default', None))


class _BaseSubTypeGetter(object):

    @staticmethod
    def getSubType(_):
        return None


class _ItemsSubTypeGetter(_BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        items = bonus.getItems().keys()
        item = first(items)
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            if item.isTrophy:
                return _HelperConsts.TROPHY_DEVICE_TYPE
            if item.isModernized:
                return _HelperConsts.MODERNIZED_DEVICE_TYPE
            return _HelperConsts.OPTIONAL_DEVICE_TYPE
        if item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            return _HelperConsts.CONSUMABLE_TYPE
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            if item.isCrewBooster():
                return _HelperConsts.CREW_BATTLE_BOOSTER_TYPE
            return _HelperConsts.DEVICE_BATTLE_BOOSTER_TYPE


class _CustomizationSubTypeGetter(_BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        customizations = bonus.getCustomizations()
        itemData = first(customizations)
        c11nItem = bonus.getC11nItem(itemData)
        itemType = c11nItem.itemTypeName
        if itemType == 'style':
            if c11nItem.isLockedOnVehicle:
                return _HelperConsts.LOCKED_STYLE
            if c11nItem.is3D:
                return _HelperConsts.STYLE_3D_TYPE
        return itemType


class _CurrenciesSubTypeGetter(_BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        return str(bonus.getCode())


_SUB_TYPE_GETTERS_MAP = {'default': _BaseSubTypeGetter,
 'items': _ItemsSubTypeGetter,
 'customizations': _CustomizationSubTypeGetter,
 'currencies': _CurrenciesSubTypeGetter}

class _BaseValueGetter(object):

    @classmethod
    def getValue(cls, bonus, _):
        return None


class _IntCDValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        keys = bonus.getValue().keys()
        value = str(first(keys))
        return value


class _BlueprintValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, source):
        intCD = bonus.getValue()[0]
        if isinstance(bonus, (IntelligenceBlueprintBonus, NationalBlueprintBonus)):
            for key in source.keys():
                if key not in BonusesLayoutConsts.MAIN_KEYS:
                    if intCD == cls.__transformKey(key, bonus):
                        return key

        return str(intCD)

    @staticmethod
    def __transformKey(key, bonus):
        intCD = int(key)
        if isinstance(bonus, IntelligenceBlueprintBonus):
            return getVehicleCDForIntelligence(intCD)
        return getVehicleCDForNational(intCD) if isinstance(bonus, NationalBlueprintBonus) else intCD


class _CustomizationValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        customizations = bonus.getCustomizations()
        itemData = first(customizations)
        return str(itemData.get('id', ''))


class _VehiclesValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        value = bonus.getValue()
        if isinstance(value, list):
            value = first(value)
        keys = value.keys()
        value = str(first(keys))
        return value


class _TokenValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        return first(bonus.getTokens().iterkeys(), '')


_VALUE_GETTERS_MAP = {'default': _BaseValueGetter,
 'blueprints': _BlueprintValueGetter,
 'items': _IntCDValueGetter,
 'goodies': _IntCDValueGetter,
 'crewBooks': _IntCDValueGetter,
 'customizations': _CustomizationValueGetter,
 'vehicles': _VehiclesValueGetter,
 'tokens': _TokenValueGetter}

class _HelperConsts(object):
    OPTIONAL_DEVICE_TYPE = 'optionalDevice'
    TROPHY_DEVICE_TYPE = 'trophyDevice'
    MODERNIZED_DEVICE_TYPE = 'modernizedDevice'
    CONSUMABLE_TYPE = 'consumable'
    CREW_BATTLE_BOOSTER_TYPE = 'crewBattleBooster'
    DEVICE_BATTLE_BOOSTER_TYPE = 'deviceBattleBooster'
    STYLE_3D_TYPE = 'style3D'
    LOCKED_STYLE = 'lockedStyle'
