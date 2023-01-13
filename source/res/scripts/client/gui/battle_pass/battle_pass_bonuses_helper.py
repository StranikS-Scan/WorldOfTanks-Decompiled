# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_bonuses_helper.py
import logging
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.formatters import text_styles
from helpers import i18n
from gui import makeHtmlString
from gui.server_events.bonuses import IntelligenceBlueprintBonus, NationalBlueprintBonus, DossierBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.blueprints_requester import getVehicleCDForIntelligence, getVehicleCDForNational
from gui.battle_pass.battle_pass_constants import BonusesLayoutConsts
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus, VehicleBlueprintBonus, ItemsBonus, CustomizationsBonus, BattlePassSelectTokensBonus, BattlePassStyleProgressTokenBonus
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
        items = bonus.getItems().keys()
        item = first(items)
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            subType = _HelperConsts.TROPHY_DEVICE_TYPE if item.isTrophy else _HelperConsts.OPTIONAL_DEVICE_TYPE
        elif item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            subType = _HelperConsts.EQUIPMENT_TYPE
        elif item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            subType = _HelperConsts.EQUIPMENT_TYPE
        return subType


class _CustomizationSubTypeGetter(_BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        customizations = bonus.getCustomizations()
        itemData = first(customizations)
        return itemData.get('custType', '')


class _RewardSelectSubTypeGetter(_BaseSubTypeGetter):

    @staticmethod
    def getSubType(bonus):
        return bonus.getType()


_SUB_TYPE_GETTERS_MAP = {'default': _BaseSubTypeGetter,
 'items': _ItemsSubTypeGetter,
 'customizations': _CustomizationSubTypeGetter,
 'battlePassSelectToken': _RewardSelectSubTypeGetter}

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


class _StyleProgressTokenValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        level = bonus.getLevel()
        return str(level)


class _VehiclesValueGetter(_BaseValueGetter):

    @classmethod
    def getValue(cls, bonus, _):
        value = bonus.getValue()
        if isinstance(value, list):
            value = first(value)
        keys = value.keys()
        value = str(first(keys))
        return value


_VALUE_GETTERS_MAP = {'default': _BaseValueGetter,
 'blueprints': _BlueprintValueGetter,
 'items': _IntCDValueGetter,
 'goodies': _IntCDValueGetter,
 'crewBooks': _IntCDValueGetter,
 'customizations': _CustomizationValueGetter,
 'styleProgressToken': _StyleProgressTokenValueGetter,
 'vehicles': _VehiclesValueGetter}

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


class _SelectTokenTextGetter(_BaseTextGetter):

    @classmethod
    def getText(cls, item):
        nameRes = R.strings.battle_pass.chosenBonuses.bonus.dyn(item.getType())
        return text_styles.main(backport.text(nameRes())) if nameRes.exists() else ''


class _StyleProgressTokenTextGetter(_BaseTextGetter):

    @classmethod
    def getText(cls, item):
        from gui.battle_pass.battle_pass_helpers import getStyleForChapter
        chapter = item.getChapter()
        level = item.getLevel()
        style = getStyleForChapter(chapter)
        text = backport.text(R.strings.battle_pass.styleProgressBonus(), styleName=style.userName, level=level)
        return text


class _TankmanTokenTextGetter(_BaseTextGetter):

    @classmethod
    def getText(cls, item):
        for tokenID in item.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                recruitInfo = getRecruitInfo(tokenID)
                if recruitInfo is not None:
                    return text_styles.main(backport.text(R.strings.battle_pass.universalTankmanBonus(), name=recruitInfo.getFullUserName()))

        return ''


_TEXT_GETTERS_MAP = {'default': _BaseTextGetter,
 'crewBooks': _CrewBookTextGetter,
 'crewSkins': _CrewSkinTextGetter,
 'dossier': _DossierTextGetter,
 'battlePassSelectToken': _SelectTokenTextGetter,
 'styleProgressToken': _StyleProgressTokenTextGetter,
 'tmanToken': _TankmanTokenTextGetter}

class _HelperConsts(object):
    HTML_BONUS_PATH = 'html_templates:lobby/quests/bonuses'
    CREW_BOOK_KEY = 'crewBookText'
    CREW_SKIN_KEY = 'crewSkinText'
    ACHIVE_KEY = 'dossierAchive'
    BADGE_KEY = 'dossierBadge'
    ACHIVE_TYPE = 'achive'
    BADGE_TYPE = 'badge'
    OPTIONAL_DEVICE_TYPE = 'optionalDevice'
    TROPHY_DEVICE_TYPE = 'trophyDevice'
    EQUIPMENT_TYPE = 'equipment'
