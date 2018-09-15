# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/formatters.py
import re
import types
from collections import namedtuple
import BigWorld
import ArenaType
from constants import ARENA_BONUS_TYPE
from gui import makeHtmlString
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles, icons
from gui.shared.money import Currency
from helpers import i18n
from shared_utils import CONST_CONTAINER
COMPLEX_TOKEN_TEMPLATE = 'img:(?P<styleID>.+):(?P<webID>.+)'
TokenComplex = namedtuple('TokenComplex', 'isDisplayable styleID webID')
MARATHON_PREFIX = 'marathon:'

def isMarathon(eventID):
    """ Determines whether given event is a based on its ID.
    
    In case of groups, True means that group is a marathon.
    In case of quest, True means that quest is marathon's main quest.
    """
    return eventID.startswith(MARATHON_PREFIX)


def getLinkedActionID(groupID, actions):
    """
    Gets linked action ID from group ID
    """
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
    if type(uiElement_or_list) is list:
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
    if type(value) not in types.StringTypes:
        value = BigWorld.wg_getNiceNumberFormat(value)
    return makeHtmlString('html_templates:lobby/quests', 'relation', {'relation': i18n.makeString('#quests:details/relations%d/%s' % (relationI18nType, relation)),
     'value': value})


def makeUniquePath(path, name):
    return '%s.%s' % (path, name)


def formatStrDiscount(discountVal):
    dt = discountVal.discountType
    if dt == DISCOUNT_TYPE.PERCENT or dt == DISCOUNT_TYPE.TRADE_IN_PERCENT:
        if dt == DISCOUNT_TYPE.PERCENT:
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


def formatGoldPrice(value):
    value = BigWorld.wg_getIntegralFormat(value)
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2, vSpace=-4)
    return '{} {}'.format(text_styles.gold(value), icon)


def formatCreditPrice(value):
    value = BigWorld.wg_getIntegralFormat(value)
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2, vSpace=-4)
    return '{} {}'.format(text_styles.credits(value), icon)


def formatGoldPriceBig(value):
    value = BigWorld.wg_getIntegralFormat(value)
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_1, vSpace=-1)
    return '{} {}'.format(text_styles.goldTextBig(value), icon)


def formatCreditPriceBig(value):
    value = BigWorld.wg_getIntegralFormat(value)
    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_1, vSpace=-1)
    return '{} {}'.format(text_styles.creditsTextBig(value), icon)


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
    assert not (not isAvailable and showDone)
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


def packSimpleBonusesBlock(bonusesList):
    data = {'linkage': 'QuestTextAwardBlockUI',
     'items': bonusesList,
     'separator': ', ',
     'ellipsis': '..'}
    return UiElement(data)


def packVehiclesBonusBlock(label, questID):
    blockData = {'linkage': 'VehiclesBonusTextElement_UI',
     'label': label,
     'questID': questID}
    return UiElement(blockData, 'label')


def packAchieveElementByItem(item):
    """ @item is achievement gui items instance
    """
    return _packAchieveElement(item.getUserName(), item.getIcon32x32(), item.getBlock(), item.getName(), item.getValue())


def _packAchieveElement(userName, iconPath, block, record, value=0):
    """ Prepares data to send to the flash
    :param userName: i18n achievement's name
    :param iconPath: path to the smallest achievement's icon
    :param block: dossier block where achievement is placed
    :param record: achievement unique name within dossier's block
    :param value: optional for tooltip, just for showing correct user text and image
    """
    return _packIconTextElement(label=userName, icon=iconPath, dataType='battleStatsAchievementData', dataValue=[block, record, value])


def packCustomizations(list):
    return UiElement({'linkage': 'CustomizationsBlock_UI',
     'list': list})


ProgressData = namedtuple('ProgressData', 'rendererLinkage, progressList')

def packProgressData(rendererLinkage, progressList):
    return ProgressData(rendererLinkage, progressList)


PreFormattedCondition = namedtuple('PreForamttedCondition', 'titleData, descrData, iconKey, current, total, progressData, conditionData, progressType, sortKey')

def packMissionIconCondition(titleData, progressType, descrData, iconKey, current=None, total=None, progressData=None, conditionData=None, sortKey=''):
    return PreFormattedCondition(titleData, descrData, iconKey, current, total, progressData, conditionData, progressType, sortKey)


_IconData = namedtuple('_IconData', 'icon, iconLabel')

def packMissionBonusTypeElements(bonusTypes, width=24, height=24, vSpace=-9):
    uniqueTypes = getUniqueBonusTypes(bonusTypes)
    elements = []
    for bonusType in uniqueTypes:
        label = i18n.makeString('#menu:bonusType/%d' % bonusType)
        icon = icons.makeImageTag(RES_ICONS.getBrebattleConditionIcon(bonusType), width=width, height=height, vSpace=vSpace)
        elements.append(_IconData(icon, label))

    return elements


def packMissionFormationElement(formationName, width=24, height=24, vSpace=-9):
    return _IconData(icons.makeImageTag(RES_ICONS.getBrebattleConditionIcon(formationName), width=width, height=height, vSpace=vSpace), i18n.makeString('#quests:details/conditions/formation/%s' % formationName))


def getUniqueBonusTypes(bonusTypes):
    uniqueTypes = set()
    for bonusType in bonusTypes:
        if bonusType in (ARENA_BONUS_TYPE.SANDBOX, ARENA_BONUS_TYPE.RATED_SANDBOX):
            bonusType = ARENA_BONUS_TYPE.RATED_SANDBOX
        if bonusType in (ARENA_BONUS_TYPE.TOURNAMENT_REGULAR, ARENA_BONUS_TYPE.TOURNAMENT_CLAN):
            bonusType = ARENA_BONUS_TYPE.TOURNAMENT
        uniqueTypes.add(bonusType)

    return uniqueTypes


def packMissionPrebattleCondition(label, icons='', tooltip=''):
    if icons:
        label = text_styles.concatStylesWithSpace(icons, label)
    return {'label': label,
     'tooltip': tooltip}


def packMissionCamoElement(camoTypeName, width=24, height=24, vSpace=-9):
    return _IconData(icons.makeImageTag(RES_ICONS.getBrebattleConditionIcon(camoTypeName), width=width, height=height, vSpace=vSpace), i18n.makeString('#quests:details/conditions/mapsType/%s' % camoTypeName))


def packMissionkMapElement(arenaTypeID):
    mapName = getMapName(arenaTypeID)
    return _IconData('', mapName) if mapName else mapName


def getMapName(arenaTypeID):
    if arenaTypeID not in ArenaType.g_cache:
        assert arenaTypeID in ArenaType.g_cache
        return None
    else:
        arenaType = ArenaType.g_cache[arenaTypeID]
        if arenaType.gameplayName != 'ctf':
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


def simpleFormat(title):
    return i18n.makeString(title)


def minimizedTitleFormat(title):
    return text_styles.stats(title)


def _titleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    if value is not None:
        relation = relation or 'equal'
        if type(value) not in types.StringTypes:
            value = BigWorld.wg_getNiceNumberFormat(value)
        relation = i18n.makeString('#quests:details/relations%s/%s' % (relationI18nType, relation))
        return '%s %s' % (relation, value)
    elif titleKey:
        return i18n.makeString(titleKey)
    else:
        return i18n.makeString(QUESTS.DETAILS_CONDITIONS_TARGET_TITLE)
        return


def titleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return text_styles.promoSubTitle(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def personalTitleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return i18n.makeString(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def personalTitleComplexRelationFormat(value, relation, titleKey=None):
    return i18n.makeString(_titleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey))


def titleComplexRelationFormat(value, relation, titleKey=None):
    return titleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey) + icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 8, -4)


def minimizedTitleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return text_styles.stats(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def minimizedTitleComplexRelationFormat(value, relation, titleKey=None):
    return minimizedTitleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey) + icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 2, -4)


def titleCumulativeFormat(current, total):
    return text_styles.promoSubTitle('%s / %s' % (BigWorld.wg_getNiceNumberFormat(int(current)), BigWorld.wg_getNiceNumberFormat(int(total))))


def personalTitleCumulativeFormat(current, total):
    return i18n.makeString('%s / %s' % (BigWorld.wg_getNiceNumberFormat(int(current)), BigWorld.wg_getNiceNumberFormat(int(total))))


def minimizedTitleCumulativeFormat(current, total):
    if current == total:
        current = text_styles.bonusAppliedText(BigWorld.wg_getNiceNumberFormat(int(current)))
    else:
        current = text_styles.stats(BigWorld.wg_getNiceNumberFormat(int(current)))
    total = text_styles.standard(int(total))
    return text_styles.disabled('%s / %s' % (current, total))


def titleComplexFormat(current, total):
    return titleCumulativeFormat(current, total) + icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 8, -4)


def minimizedTitleComplexFormat(current, total):
    return minimizedTitleCumulativeFormat(current, total) + icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 2, -4)


def getAchievementsConditionKey(condition):
    key = 'oneAchievement' if len(condition.getValue()) == 1 else 'achievements'
    if condition.isNegative():
        key = '%s/not' % key
    return key


def actionTitleFormat(title):
    return text_styles.titleFont(title)
