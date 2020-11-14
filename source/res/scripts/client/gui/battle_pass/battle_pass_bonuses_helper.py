# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_bonuses_helper.py
import logging
import weakref
import typing
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BattlePassConsts, BattlePassState
from helpers import i18n, dependency
from gui import makeHtmlString
from gui.server_events.bonuses import IntelligenceBlueprintBonus, NationalBlueprintBonus, DossierBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from items import vehicles
from gui.shared.utils.requesters.blueprints_requester import getVehicleCDForIntelligence, getVehicleCDForNational
from gui.battle_pass.battle_pass_consts import BonusesLayoutConsts
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus, VehicleBlueprintBonus, CustomizationsBonus
    from skeletons.gui.game_control import IBattlePassController
_logger = logging.getLogger(__name__)
TROPHY_GIFT_TOKEN_BONUS_NAME = 'battlePassTrophyGiftToken'
NEW_DEVICE_GIFT_TOKEN_BONUS_NAME = 'battlePassNewDeviceGiftToken'

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
        return result[parameter] if parameter in result else defaultValue

    @classmethod
    def getTextStrings(cls, bonus):
        getter = cls.__selectGetter(bonus, _TEXT_GETTERS_MAP)
        if getter is None:
            return []
        else:
            result = []
            items = getter.getItems(bonus)
            for item in items:
                result.append(getter.getText(item))

            return result

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
        name = bonus.getName()
        return getters[name] if name in getters else getters.get('default', None)


class _BaseSubTypeGetter(object):

    @staticmethod
    def getSubType(_):
        return None


class _ItemsSubTypeGetter(_BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        subType = ''
        keys = bonus.getValue().keys()
        intCD = first(keys)
        itemTypeID, _, _ = vehicles.parseIntCompactDescr(intCD)
        if itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            subType = _HelperConsts.OPTIONAL_DEVICE_TYPE
        elif itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            subType = _HelperConsts.EQUIPMENT_TYPE
        return subType


class _CustomizationSubTypeGetter(_BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        customizations = bonus.getCustomizations()
        itemData = first(customizations)
        return itemData.get('custType', '')


_SUB_TYPE_GETTERS_MAP = {'default': _BaseSubTypeGetter,
 'items': _ItemsSubTypeGetter,
 'customizations': _CustomizationSubTypeGetter}

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
            intCD = getVehicleCDForIntelligence(intCD)
        elif isinstance(bonus, NationalBlueprintBonus):
            intCD = getVehicleCDForNational(intCD)
        return intCD


class _CustomizationValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        customizations = bonus.getCustomizations()
        itemData = first(customizations)
        return str(itemData.get('id', ''))


_VALUE_GETTERS_MAP = {'default': _BaseValueGetter,
 'blueprints': _BlueprintValueGetter,
 'items': _IntCDValueGetter,
 'goodies': _IntCDValueGetter,
 'crewBooks': _IntCDValueGetter,
 'customizations': _CustomizationValueGetter}

class _BaseTextGetter(object):

    @staticmethod
    def getItems(bonus):
        return [bonus]

    @classmethod
    def getText(cls, item):
        return item.format()


class _HtmlTextGetter(_BaseTextGetter):

    @classmethod
    def getText(cls, item):
        path = cls._getPath()
        key = cls._getKey(item)
        context = cls._getContext(item)
        return makeHtmlString(path, key, context)

    @staticmethod
    def _getPath():
        return _HelperConsts.HTML_BONUS_PATH

    @staticmethod
    def _getKey(_):
        pass

    @staticmethod
    def _getContext(_):
        return {}


class _CrewBookTextGetter(_HtmlTextGetter):

    @staticmethod
    def getItems(bonus):
        return bonus.getItems()

    @staticmethod
    def _getKey(_):
        return _HelperConsts.CREW_BOOK_KEY

    @staticmethod
    def _getContext(crewBook):
        item, count = crewBook
        return {'type': item.getBookType(),
         'nation': item.getNation(),
         'value': count,
         'name': item.userName}


class _CrewSkinTextGetter(_HtmlTextGetter):

    @staticmethod
    def getItems(bonus):
        sortedByRarity = {}
        for item, count, _, _ in bonus.getItems():
            if count:
                rarity = item.getRarity()
                totalCount = sortedByRarity.setdefault(rarity, 0)
                firstName = item.getFirstName()
                lastName = item.getLastName()
                sortedByRarity[rarity] = (totalCount + count, firstName, lastName)

        return [ (count, firstNameID, lastNameID) for _, (count, firstNameID, lastNameID) in sortedByRarity.iteritems() ]

    @staticmethod
    def _getKey(_):
        return _HelperConsts.CREW_SKIN_KEY

    @staticmethod
    def _getContext(item):
        count, firstNameID, lastNameID = item
        firstName = i18n.makeString(firstNameID)
        lastName = i18n.makeString(lastNameID)
        return {'value': count,
         'firstName': firstName,
         'lastName': lastName}


class _DossierTextGetter(_HtmlTextGetter):

    @staticmethod
    def getItems(bonus):
        result = [ (achive, _HelperConsts.ACHIVE_TYPE) for achive in bonus.getAchievements() ]
        result.extend([ (badge, _HelperConsts.BADGE_TYPE) for badge in bonus.getBadges() ])
        return result

    @staticmethod
    def _getKey(item):
        _, typeItem = item
        if typeItem == _HelperConsts.ACHIVE_TYPE:
            return _HelperConsts.ACHIVE_KEY
        return _HelperConsts.BADGE_KEY if typeItem == _HelperConsts.BADGE_TYPE else ''

    @staticmethod
    def _getContext(item):
        achive, _ = item
        return {'name': achive.getUserName()}


_TEXT_GETTERS_MAP = {'default': _BaseTextGetter,
 'crewBooks': _CrewBookTextGetter,
 'crewSkins': _CrewSkinTextGetter,
 'dossier': _DossierTextGetter}

class _HelperConsts(object):
    HTML_BONUS_PATH = 'html_templates:lobby/quests/bonuses'
    CREW_BOOK_KEY = 'crewBookText'
    CREW_SKIN_KEY = 'crewSkinText'
    ACHIVE_KEY = 'dossierAchive'
    BADGE_KEY = 'dossierBadge'
    ACHIVE_TYPE = 'achive'
    BADGE_TYPE = 'badge'
    OPTIONAL_DEVICE_TYPE = 'optionalDevice'
    EQUIPMENT_TYPE = 'equipment'


class DeviceTokensContainer(object):

    def __init__(self, battlePassController, bonusName):
        self.__battlePassController = weakref.proxy(battlePassController)
        self.__bonusName = bonusName
        self.__freeTokenPositions = []
        self.__paidTokenPositions = []

    @property
    def freeTokenPositions(self):
        return self.__freeTokenPositions

    @property
    def paidTokenPositions(self):
        return self.__paidTokenPositions

    @property
    def isEmpty(self):
        return not bool(self.__freeTokenPositions or self.__paidTokenPositions)

    def addFreeTokenPos(self, position):
        self.__freeTokenPositions.append(position)

    def addPaidTokenPos(self, position):
        self.__paidTokenPositions.append(position)

    def getFreeAvailableTokens(self):
        currentLevel = self.__getBaseProgressionCurrentLevel()
        return [ 0 <= pos <= currentLevel for pos in self.__freeTokenPositions ]

    def getPaidAvailableTokens(self):
        currentLevel = self.__getBaseProgressionCurrentLevel()
        if not self.__battlePassController.isBought():
            return [False] * len(self.__paidTokenPositions)
        return [ 0 <= pos <= currentLevel for pos in self.__paidTokenPositions ]

    def saveChosenToken(self):
        settingsCore = dependency.instance(ISettingsCore)
        freeAvailableTokens = self.getFreeAvailableTokens()
        paidAvailableTokens = self.getPaidAvailableTokens()
        savedUsedTokens = settingsCore.serverSettings.getBPStorage().get(_getStorageKey(self.__bonusName))
        usedToken = 0
        for offset, isTokenAvailable in enumerate(freeAvailableTokens + paidAvailableTokens):
            if not isTokenAvailable:
                continue
            usedToken = 1 << offset
            if savedUsedTokens & usedToken == 0:
                if BattlePassStorageKeys.MASK_CHOSEN_DEVICES & usedToken == 0:
                    _logger.error('[Battle Pass] Base reward config has more "%s" tokens than storage')
                    return
                break

        settingsCore.serverSettings.saveInBPStorage({_getStorageKey(self.__bonusName): savedUsedTokens | usedToken})

    def isTokenUsed(self, level, awardType):
        settingsCore = dependency.instance(ISettingsCore)
        savedUsedTokens = settingsCore.serverSettings.getBPStorage().get(_getStorageKey(self.__bonusName))
        if awardType == BattlePassConsts.REWARD_PAID and level in self.__paidTokenPositions:
            offset = self.__paidTokenPositions.index(level) + len(self.__freeTokenPositions)
            return savedUsedTokens & 1 << offset > 0
        if awardType == BattlePassConsts.REWARD_FREE and level in self.__freeTokenPositions:
            offset = self.__freeTokenPositions.index(level)
            return savedUsedTokens & 1 << offset > 0
        _logger.warning('%s must not be in awardType=%s.', self.__bonusName, awardType)
        return False

    def getUnusedTokensCount(self):
        settingsCore = dependency.instance(ISettingsCore)
        freeAvailableTokens = self.getFreeAvailableTokens()
        paidAvailableTokens = self.getPaidAvailableTokens()
        savedUsedTokens = settingsCore.serverSettings.getBPStorage().get(_getStorageKey(self.__bonusName))
        count = 0
        for offset, isTokenAvailable in enumerate(freeAvailableTokens + paidAvailableTokens):
            if not isTokenAvailable:
                continue
            usedToken = 1 << offset
            if savedUsedTokens & usedToken == 0:
                count += 1

        return count

    def clear(self):
        self.__freeTokenPositions = []
        self.__paidTokenPositions = []

    def __getBaseProgressionCurrentLevel(self):
        return self.__battlePassController.getMaxLevel() if not self.__battlePassController.getState() == BattlePassState.BASE else self.__battlePassController.getCurrentLevel()


def _getStorageKey(bonusName):
    if bonusName == TROPHY_GIFT_TOKEN_BONUS_NAME:
        return BattlePassStorageKeys.CHOSEN_TROPHY_DEVICES
    return BattlePassStorageKeys.CHOSEN_NEW_DEVICES if bonusName == NEW_DEVICE_GIFT_TOKEN_BONUS_NAME else ''
