# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/formatters.py
import re
import types
from collections import namedtuple
import logging
import ArenaType
from constants import ARENA_BONUS_TYPE, GAMEPLAY_NAMES_WITH_DISABLED_QUESTS
from gui import makeHtmlString
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.settings import ICONS_SIZES
from gui.impl import backport
from gui.Scaleform.genConsts.QUEST_AWARD_BLOCK_ALIASES import QUEST_AWARD_BLOCK_ALIASES
from gui.shared.formatters import text_styles, icons as gui_icons
from gui.shared.money import Currency
from helpers import i18n
from shared_utils import CONST_CONTAINER
COMPLEX_TOKEN = 'complex_token'
COMPLEX_TOKEN_TEMPLATE = 'img:(?P<styleID>.+):(?P<webID>.+)'
TokenComplex = namedtuple('TokenComplex', 'isDisplayable styleID webID')
_logger = logging.getLogger(__name__)

def getLinkedActionID(groupID, actions):
    delimiter = ':'
    if groupID and delimiter in groupID:
        splittedGroup = groupID.split(delimiter)
        splitID = splittedGroup[-1]
        if splittedGroup and splitID in actions:
            return splitID
    return None


def parseComplexToken(tokenID):
    match = re.match(COMPLEX_TOKEN_TEMPLATE, tokenID)
    return TokenComplex(True, match.group('styleID'), match.group('webID')) if match else TokenComplex(False, '', '')


class DISCOUNT_TYPE(CONST_CONTAINER):
    PERCENT = 'percent'
    GOLD = Currency.GOLD
    CREDITS = Currency.CREDITS
    CRYSTAL = Currency.CRYSTAL
    EVENT_COIN = Currency.EVENT_COIN
    XP = 'xp'
    FREE_XP = 'freeXp'
    MULTIPLIER = 'multiplier'
    TRADE_IN_PERCENT = 'trade_in_percent'


class PROGRESS_BAR_TYPE(CONST_CONTAINER):
    STRATEGIC = 'strategic'
    SIMPLE = 'current'
    COMMON = 'common'
    ACTION = 'action'
    NONE = ''


class RELATIONS(CONST_CONTAINER):
    GT = 'greater'
    LS = 'less'
    EQ = 'equal'
    NEQ = 'notEqual'
    LSQ = 'lessOrEqual'
    GTQ = 'greaterOrEqual'
    _OPPOSITE = {GT: LSQ,
     LS: GTQ,
     EQ: NEQ,
     NEQ: EQ,
     LSQ: GT,
     GTQ: LS}

    @classmethod
    def getOppositeRelation(cls, relation):
        return cls._OPPOSITE.get(relation)


class RELATIONS_SCHEME(CONST_CONTAINER):
    DEFAULT = 1
    ALTERNATIVE = 2


class TOKEN_SIZES(CONST_CONTAINER):
    SMALL = '48x48'
    MEDIUM = '60x60'
    BIG = '80x80'


class DECORATION_SIZES(CONST_CONTAINER):
    MARATHON = '1024x116'
    CARDS = '482x222'
    BONUS = '300x110'
    DISCOUNT = '480x280'
    DETAILS = '750x264'
    DAILY = 'N/A'


class UiElement(object):

    def __init__(self, initDict, labelFieldName=None):
        self._dict = initDict
        self._labelFieldName = labelFieldName
        self._originalLabel = self._dict.get(self._labelFieldName)

    def getDict(self):
        return self._dict

    def getLabel(self):
        return self._dict[self._labelFieldName] if self._labelFieldName is not None else None

    def setIndex(self, index):
        if self._labelFieldName is not None and self._labelFieldName in self._dict:
            self._dict[self._labelFieldName] = formatIndex(index, self._dict[self._labelFieldName])
            return True
        else:
            return False

    def removeIndex(self):
        if self._labelFieldName is not None and self._labelFieldName in self._dict:
            self._dict[self._labelFieldName] = self._originalLabel
        return


def todict(uiElement_or_list):
    if isinstance(uiElement_or_list, list):
        return [ uiE._dict for uiE in uiElement_or_list ]
    return uiElement_or_list._dict


def indexing(uiElements, startIndex=1, step=1):
    index = startIndex
    for fmt in uiElements:
        if fmt.setIndex(index):
            index += step

    return uiElements


def _packIconTextElement(label='', icon='', dataType=None, dataValue=None, counter='', iconAutoSize=True):
    return UiElement({'linkage': 'QuestIconElement_UI',
     'label': label,
     'icon': icon,
     'dataType': dataType,
     'dataValue': dataValue,
     'counter': counter,
     'iconAutoSize': iconAutoSize}, 'label')


def formatRelation(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT):
    relation = relation or 'equal'
    if not isinstance(value, types.StringTypes):
        value = backport.getNiceNumberFormat(value)
    return makeHtmlString('html_templates:lobby/quests', 'relation', {'relation': i18n.makeString('#quests:details/relations%d/%s' % (relationI18nType, relation)),
     'value': value})


def makeUniquePath(path, name):
    return '%s.%s' % (path, name)


def formatStrDiscount(discountVal):
    dt = discountVal.discountType
    dn = discountVal.discountName
    if dt == DISCOUNT_TYPE.PERCENT or dt == DISCOUNT_TYPE.TRADE_IN_PERCENT:
        if dt == DISCOUNT_TYPE.PERCENT:
            if isinstance(dn, types.StringTypes) and dn == 'marathon':
                txtKey = QUESTS.ACTION_DISCOUNT_DISCOUNTUPTOTEXT
            else:
                txtKey = QUESTS.ACTION_DISCOUNT_DISCOUNTTEXT
        else:
            txtKey = QUESTS.ACTION_DISCOUNT_TRADEINLABELTEXT
        return '{} {}'.format(i18n.makeString(txtKey), i18n.makeString(QUESTS.ACTION_DISCOUNT_PERCENT, value=discountVal.discountValue))
    if dt == DISCOUNT_TYPE.MULTIPLIER:
        return i18n.makeString(QUESTS.ACTION_DISCOUNT_MODIFIER, count=discountVal.discountValue)
    if dt == DISCOUNT_TYPE.GOLD:
        return formatGoldPrice(discountVal.discountValue)
    return formatCreditPrice(discountVal.discountValue) if dt == DISCOUNT_TYPE.CREDITS else ''


def formatMultiplierValue(value):
    return makeHtmlString('html_templates:lobby/quests/actions', 'multiplier', {'value': value})


def formatPercentValue(value):
    return makeHtmlString('html_templates:lobby/quests/actions', 'percent', {'value': value})


def formatVehicleLevel(value):
    return makeHtmlString('html_templates:lobby/quests/actions', 'vehicleLevel', {'value': value})


def formatCreditPriceNormalCard(value):
    value = backport.getIntegralFormat(value)
    icon = gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1, vSpace=-1)
    return '{} {}'.format(text_styles.creditsTextNormalCard(value), icon)


def formatGoldPriceNormalCard(value):
    value = backport.getIntegralFormat(value)
    icon = gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1, vSpace=-1)
    return '{} {}'.format(text_styles.goldTextNormalCard(value), icon)


def formatGoldPrice(value):
    value = backport.getIntegralFormat(value)
    icon = gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2, vSpace=-4)
    return '{} {}'.format(text_styles.gold(value), icon)


def formatCreditPrice(value):
    value = backport.getIntegralFormat(value)
    icon = gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2, vSpace=-4)
    return '{} {}'.format(text_styles.credits(value), icon)


def formatGoldPriceBig(value):
    value = backport.getIntegralFormat(value)
    icon = gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1, vSpace=-1)
    return '{} {}'.format(text_styles.goldTextBig(value), icon)


def formatCreditPriceBig(value):
    value = backport.getIntegralFormat(value)
    icon = gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1, vSpace=-1)
    return '{} {}'.format(text_styles.creditsTextBig(value), icon)


def formatCrystalPrice(value):
    value = backport.getIntegralFormat(value)
    icon = gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CRYSTALICON_2, vSpace=-4)
    return '{} {}'.format(text_styles.crystal(value), icon)


def formatYellow(msg, *args, **kwargs):
    return makeHtmlString('html_templates:lobby/quests', 'yellowTemplate', {'msg': i18n.makeString(msg, *args, **kwargs)})


def formatGold(msg, *args, **kwargs):
    return makeHtmlString('html_templates:lobby/quests', 'goldTemplate', {'msg': i18n.makeString(msg, *args, **kwargs)})


def formatIndex(index, msg):
    return makeHtmlString('html_templates:lobby/quests', 'index', {'index': index,
     'label': msg})


def packTextBlock(label, value=None, relation=None, questID=None, isAvailable=True, fullLabel=None, counterValue=0, showDone=False, relationI18nType=RELATIONS_SCHEME.DEFAULT, counterDescr=None):
    if value is not None:
        value = formatRelation(value, relation, relationI18nType)
    if counterDescr is None:
        counterDescr = i18n.makeString('#quests:quests/table/amount')
    blockData = {'linkage': 'CounterTextElement_UI',
     'label': label,
     'fullLabel': fullLabel,
     'value': value,
     'linkID': questID,
     'isNotAvailable': not isAvailable,
     'counterValue': counterValue,
     'counterDescr': counterDescr,
     'showDone': showDone}
    return UiElement(blockData, 'label')


def packSimpleBonusesBlock(bonusesList, endlineSymbol=''):
    data = {'linkage': 'QuestTextAwardBlockUI',
     'items': bonusesList,
     'separator': ', ',
     'ellipsis': '..',
     'endline': endlineSymbol}
    return UiElement(data)


def packNewStyleBonusesBlock(bonusesList, endlineSymbol=''):
    data = {'linkage': QUEST_AWARD_BLOCK_ALIASES.QUEST_BIG_ICON_AWARD_BLOCK,
     'items': bonusesList,
     'separator': ', ',
     'ellipsis': '..',
     'endline': endlineSymbol,
     'showInNewLine': False}
    return UiElement(data)


def packVehiclesBonusBlock(label, questID):
    blockData = {'linkage': 'VehiclesBonusTextElement_UI',
     'label': label,
     'questID': questID}
    return UiElement(blockData, 'label')


def packAchieveElementByItem(item):
    return _packAchieveElement(item.getUserName(), item.getIcon32x32(), item.getBlock(), item.getName(), item.getValue())


def packBadgeElementByItem(item):
    return _packAchieveElement(item.getUserName(), item.getAwardBadgeIcon(ICONS_SIZES.X24), None, item.getName())


def _packAchieveElement(userName, iconPath, block, record, value=0):
    return _packIconTextElement(label=userName, icon=iconPath, dataType='battleStatsAchievementData', dataValue=[block, record, value])


def packCustomizations(elements):
    return UiElement({'linkage': 'CustomizationsBlockUI',
     'list': elements})


ProgressData = namedtuple('ProgressData', 'rendererLinkage, progressList')

def packProgressData(rendererLinkage, progressList):
    return ProgressData(rendererLinkage, progressList)


PreFormattedCondition = namedtuple('PreForamttedCondition', 'titleData, descrData, iconKey, current, total, earned, progressData, conditionData,progressType, sortKey, progressID')

def packMissionIconCondition(titleData, progressType, descrData, iconKey, current=None, total=None, earned=None, progressData=None, conditionData=None, sortKey='', progressID=None):
    return PreFormattedCondition(titleData, descrData, iconKey, current, total, earned, progressData, conditionData, progressType, sortKey, progressID)


_IconData = namedtuple('_IconData', 'icon, iconLabel')

def packMissionBonusTypeElements(bonusTypes, width=32, height=32, vSpace=-11):
    uniqueTypes = getUniqueBonusTypes(bonusTypes)
    elements = []
    for bonusType in uniqueTypes:
        label = i18n.makeString('#menu:bonusType/%d' % bonusType)
        icon = gui_icons.makeImageTag(RES_ICONS.getBrebattleConditionIcon(bonusType), width=width, height=height, vSpace=vSpace)
        elements.append(_IconData(icon, label))

    return elements


def packMissionFormationElement(formationName, width=32, height=32, vSpace=-11):
    return _IconData(gui_icons.makeImageTag(RES_ICONS.getBrebattleConditionIcon(formationName), width=width, height=height, vSpace=vSpace), i18n.makeString('#quests:details/conditions/formation/%s' % formationName))


def getUniqueBonusTypes(bonusTypes):
    uniqueTypes = set()
    for bonusType in bonusTypes:
        if bonusType in (ARENA_BONUS_TYPE.SANDBOX, ARENA_BONUS_TYPE.RATED_SANDBOX):
            bonusType = ARENA_BONUS_TYPE.RATED_SANDBOX
        if bonusType in ARENA_BONUS_TYPE.TOURNAMENT_RANGE:
            bonusType = ARENA_BONUS_TYPE.TOURNAMENT
        if bonusType in (ARENA_BONUS_TYPE.EPIC_RANDOM_TRAINING, ARENA_BONUS_TYPE.EPIC_BATTLE_TRAINING):
            bonusType = ARENA_BONUS_TYPE.EPIC_RANDOM
        if bonusType in (ARENA_BONUS_TYPE.BOOTCAMP,):
            bonusType = ARENA_BONUS_TYPE.REGULAR
        if bonusType in (ARENA_BONUS_TYPE.EVENT_BATTLES_2,):
            bonusType = ARENA_BONUS_TYPE.EVENT_BATTLES
        if bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
            bonusType = ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO
        uniqueTypes.add(bonusType)

    return uniqueTypes


def packMissionPrebattleCondition(label, icons='', tooltip=''):
    if icons:
        label = text_styles.concatStylesWithSpace(icons, label)
    return {'label': label,
     'tooltip': tooltip}


def packMissionCamoElement(camoTypeName, width=32, height=32, vSpace=-11):
    return _IconData(gui_icons.makeImageTag(RES_ICONS.getBrebattleConditionIcon(camoTypeName), width=width, height=height, vSpace=vSpace), i18n.makeString('#quests:details/conditions/mapsType/%s' % camoTypeName))


def packMissionkMapElement(arenaTypeID):
    mapName = getMapName(arenaTypeID)
    return _IconData('', mapName) if mapName else mapName


def getMapName(arenaTypeID):
    if arenaTypeID not in ArenaType.g_cache:
        return
    else:
        arenaType = ArenaType.g_cache[arenaTypeID]
        if arenaType.gameplayName != 'ctf':
            label = None
            if arenaType.gameplayName not in GAMEPLAY_NAMES_WITH_DISABLED_QUESTS:
                label = '%s (%s)' % (arenaType.name, i18n.makeString('#arenas:type/%s/name' % arenaType.gameplayName))
        else:
            label = arenaType.name
        return label


def getConditionIcon128(iconKey):
    return RES_ICONS.get128ConditionIcon(iconKey)


def getConditionIcon64(iconKey):
    return RES_ICONS.get128ConditionIcon(iconKey)


def titleFormat(title):
    return text_styles.promoSubTitle(title)


def titleFormatPlain(title):
    return text_styles.promoSubTitlePlain(title)


def simpleFormat(title):
    return i18n.makeString(title)


def minimizedTitleFormat(title):
    return text_styles.stats(title)


def _titleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    if value is not None:
        relation = relation or 'equal'
        if not isinstance(value, types.StringTypes):
            value = backport.getNiceNumberFormat(value)
        relation = i18n.makeString('#quests:details/relations%s/%s' % (relationI18nType, relation))
        return '%s %s' % (relation, value)
    elif titleKey:
        return i18n.makeString(titleKey)
    else:
        return i18n.makeString(QUESTS.DETAILS_CONDITIONS_TARGET_TITLE)
        return


def titleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return text_styles.promoSubTitle(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def titleRelationFormatPlain(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return text_styles.promoSubTitlePlain(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def personalTitleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return i18n.makeString(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def personalTitleComplexRelationFormat(value, relation, titleKey=None):
    return i18n.makeString(_titleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey))


def titleComplexRelationFormat(value, relation, titleKey=None):
    return titleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey) + gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 8, -4)


def titleComplexRelationFormatPlain(value, relation, titleKey=None):
    _logger.error('Information loss: We are loosing information about the image.')
    return titleRelationFormatPlain(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey)


def minimizedTitleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return text_styles.stats(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def minimizedTitleComplexRelationFormat(value, relation, titleKey=None):
    return minimizedTitleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey) + gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 2, -4)


def titleCumulativeFormat(current, total):
    return text_styles.promoSubTitle('%s / %s' % (backport.getNiceNumberFormat(int(current)), backport.getNiceNumberFormat(int(total))))


def titleCumulativeFormatPlain(current, total):
    return text_styles.promoSubTitlePlain('%s / %s' % (backport.getNiceNumberFormat(int(current)), backport.getNiceNumberFormat(int(total))))


def personalTitleCumulativeFormat(current, total):
    return i18n.makeString('%s / %s' % (backport.getNiceNumberFormat(int(current)), backport.getNiceNumberFormat(int(total))))


def minimizedTitleCumulativeFormat(current, total):
    if current == total:
        current = text_styles.bonusAppliedText(backport.getNiceNumberFormat(int(current)))
    else:
        current = text_styles.stats(backport.getNiceNumberFormat(int(current)))
    total = text_styles.standard(int(total))
    return text_styles.disabled('%s / %s' % (current, total))


def titleComplexFormat(current, total):
    return titleCumulativeFormat(current, total) + gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 8, -4)


def titleComplexFormatPlain(current, total):
    return titleCumulativeFormatPlain(current, total) + gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 8, -4)


def minimizedTitleComplexFormat(current, total):
    return minimizedTitleCumulativeFormat(current, total) + gui_icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 2, -4)


def getAchievementsConditionKey(condition):
    key = 'oneAchievement' if len(condition.getValue()) == 1 else 'achievements'
    if condition.isNegative():
        key = '%s/not' % key
    return key


def actionTitleFormat(title):
    return text_styles.titleFont(title)


def tagText(text, tag):
    return '{%sOpen}%s{%sClose}' % (tag, text, tag)
