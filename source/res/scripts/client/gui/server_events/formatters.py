# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/formatters.py
import re
import types
from collections import namedtuple
import ArenaType
import BigWorld
from constants import ARENA_BONUS_TYPE
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui import makeHtmlString
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import caches
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.vehicle_filters import packNationsFilter, packIntVehicleTypesFilter, packVehicleLevelsFilter
from gui.shared.money import Currency
from helpers import i18n, int2roman
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
        if len(splittedGroup) and splitID in actions:
            return splitID
    return None


def parseComplexToken(tokenID):
    match = re.match(COMPLEX_TOKEN_TEMPLATE, tokenID)
    if match:
        return TokenComplex(True, match.group('styleID'), match.group('webID'))
    else:
        return TokenComplex(False, '', '')


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


def _packTableHeaderBtn(btnID, width, label='', tooltip='', icon=None, showSeparator=True, defaultSortDirection='descending', inverted=False):
    return {'id': btnID,
     'label': label,
     'toolTip': tooltip,
     'iconSource': icon,
     'buttonWidth': width,
     'buttonHeight': 40,
     'defaultSortDirection': defaultSortDirection,
     'ascendingIconSource': '../maps/icons/buttons/tab_sort_button/ascProfileSortArrow.png',
     'descendingIconSource': '../maps/icons/buttons/tab_sort_button/descProfileSortArrow.png',
     'showSeparator': showSeparator,
     'inverted': inverted}


def _packNationBtn(width):
    return _packTableHeaderBtn('nation', width, label='', icon='../maps/icons/filters/nations/all.png', tooltip='#quests:tooltip/vehTable/nation', defaultSortDirection='ascending', inverted=True)


def _packVehTypeBtn(width):
    return _packTableHeaderBtn('type', width, label='', icon='../maps/icons/filters/tanks/all.png', tooltip='#quests:tooltip/vehTable/class')


def _packVehLevelBtn(width):
    return _packTableHeaderBtn('level', width, label='', icon='../maps/icons/buttons/tab_sort_button/level.png', tooltip='#quests:tooltip/vehTable/level')


def _packVehNameBtn(width, showSeparator=True):
    return _packTableHeaderBtn('vName', width, label='#quests:details/requirements/vehiclesTable/name', tooltip='#quests:tooltip/vehTable/name', showSeparator=showSeparator)


def _packCountBtn(width):
    return _packTableHeaderBtn('count', width, label='#quests:details/requirements/vehiclesTable/count')


def _packUnavailableBtn(width, showSeparator=True):
    return _packTableHeaderBtn('notAvailable', width, label='', icon='../maps/icons/buttons/tab_sort_button/notAvailable.png', tooltip='#quests:tooltip/vehTable/availability', showSeparator=showSeparator)


def _packDiscountBtn(width, showSeparator=True):
    return _packTableHeaderBtn('discount', width, label='#quests:details/requirements/vehiclesTable/discount', tooltip='#quests:tooltip/vehTable/discount', showSeparator=showSeparator)


VEH_KILLS_HEADER = VEH_OWNED_HEADER = VEH_UNLOCKS_HEADER = [_packNationBtn(40),
 _packVehTypeBtn(40),
 _packVehLevelBtn(40),
 _packVehNameBtn(254, showSeparator=False)]
VEH_REQUIRED_HEADER = [_packNationBtn(40),
 _packVehTypeBtn(40),
 _packVehLevelBtn(40),
 _packVehNameBtn(197),
 _packUnavailableBtn(57, showSeparator=False)]
VEH_ACTION_HEADER = [_packNationBtn(40),
 _packVehTypeBtn(40),
 _packVehLevelBtn(40),
 _packVehNameBtn(154),
 _packDiscountBtn(100, showSeparator=False)]

def _packVehicle(vehicle, isAvailable=True, discountValue=None, discoutType=None, disableChecker=None, showDone=False):
    if vehicle is None:
        return
    else:
        discount = None
        if discountValue is not None and discoutType is not None:
            discount = formatDiscount(discountValue, discoutType)
        disableChecker = disableChecker or (lambda item: False)
        return {'nationID': vehicle.nationID,
         'vIconSmall': vehicle.iconSmall,
         'vType': vehicle.type,
         'vLevel': vehicle.level,
         'vName': vehicle.shortUserName,
         'isAvailable': isAvailable,
         'isDisabled': disableChecker(vehicle),
         'progressData': None,
         'htmlLabel': discount,
         'showDone': showDone}


def _packIconTextElement(label='', icon='', dataType=None, dataValue=None, counter='', iconAutoSize=True):
    return UiElement({'linkage': 'QuestIconElement_UI',
     'label': label,
     'icon': icon,
     'dataType': dataType,
     'dataValue': dataValue,
     'counter': counter,
     'iconAutoSize': iconAutoSize}, 'label')


def _packProgress(current, total, label=''):
    return None if current is None or total is None else {'progrTooltip': None,
     'progrBarType': PROGRESS_BAR_TYPE.SIMPLE,
     'maxProgrVal': total,
     'currentProgrVal': current,
     'description': label}


def formatRelation(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT):
    relation = relation or 'equal'
    if type(value) not in types.StringTypes:
        value = BigWorld.wg_getNiceNumberFormat(value)
    return makeHtmlString('html_templates:lobby/quests', 'relation', {'relation': i18n.makeString('#quests:details/relations%d/%s' % (relationI18nType, relation)),
     'value': value})


def _packConditionsBlock(label, counterValue=None, conditions=None, showDone=False, counterDescr=None):
    if counterDescr is None:
        counterDescr = i18n.makeString('#quests:quests/table/battlesLeft')
    return UiElement({'linkage': 'CommonConditionsBlock_UI',
     'description': label,
     'counterValue': counterValue,
     'progressElements': todict(conditions or []),
     'showDone': showDone,
     'counterDescr': counterDescr}, 'description')


def _packGroupByConditionsBlock(label='', vehicle=None, counterValue=None, conditions=None, icon=None, isCompleted=False, counterDescr=None):
    if counterDescr is None:
        counterDescr = i18n.makeString('#quests:quests/table/battlesLeft')
    return UiElement({'linkage': 'EventProgressBlock_UI',
     'vehicleData': _packVehicle(vehicle),
     'iconSource': icon,
     'description': label,
     'counterValue': counterValue,
     'counterDescr': counterDescr,
     'progressElements': todict(conditions or []),
     'showDone': isCompleted}, 'description')


def packVehiclesList(vehsData, disableChecker):
    result = []
    for v, (isAvailable, discount, discoutType) in vehsData:
        result.append(_packVehicle(v, isAvailable, discount, discoutType, disableChecker))

    return result


def makeUniquePath(path, name):
    return '%s.%s' % (path, name)


def makeUniqueTableID(event, uniqueName):
    eventID = ''
    if event is not None:
        eventID = event.getID()
    return makeUniquePath(eventID, uniqueName)


def formatDiscount(discountVal, discountType):
    multiplier = '+' if discountVal < 0 else ''
    return makeHtmlString('html_templates:lobby/quests/actions', Currency.GOLD, {'value': multiplier + BigWorld.wg_getGoldFormat(abs(long(discountVal)))}) if discountType == DISCOUNT_TYPE.GOLD else makeHtmlString('html_templates:lobby/quests/actions', discountType, {'value': multiplier + BigWorld.wg_getIntegralFormat(abs(int(discountVal)))})


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


def formatGray(msg):
    return makeHtmlString('html_templates:lobby/quests', 'grayTemplate', {'msg': i18n.makeString(msg)})


def formatBright(msg):
    return makeHtmlString('html_templates:lobby/quests', 'brightTemplate', {'msg': i18n.makeString(msg)})


def formatYellow(msg, *args, **kwargs):
    return makeHtmlString('html_templates:lobby/quests', 'yellowTemplate', {'msg': i18n.makeString(msg, *args, **kwargs)})


def formatGold(msg, *args, **kwargs):
    return makeHtmlString('html_templates:lobby/quests', 'goldTemplate', {'msg': i18n.makeString(msg, *args, **kwargs)})


def formatIndex(index, msg):
    return makeHtmlString('html_templates:lobby/quests', 'index', {'index': index,
     'label': msg})


def getNationName(nation):
    assert nation is not None, 'nation must be specified'
    return i18n.makeString(MENU.nations(nation))


def packTopLevelContainer(title='', note='', subBlocks=None, isOpened=True, isResizable=False, current=None, total=None, showDone=False):
    return UiElement({'linkage': 'ResizableContent_UI',
     'headerTitle': title,
     'headerHtmlPart': note,
     'headerProgress': _packProgress(current, total),
     'containerElements': todict(subBlocks or []),
     'isOpened': isOpened,
     'isResizable': isResizable,
     'showDone': showDone})


def packContainer(title='', subBlocks=None, isOpened=True, isResizable=False, current=None, total=None, value=None, relation=None, showDone=False):
    if value is not None:
        title = '%s: %s' % (title, formatRelation(value, relation))
    return UiElement({'linkage': 'InnerResizableContent_UI',
     'headerHtmlPart': title,
     'headerProgress': _packProgress(current, total),
     'containerElements': todict(subBlocks or []),
     'isOpened': isOpened,
     'isResizable': isResizable,
     'showDone': showDone}, 'headerHtmlPart')


def packVehiclesBlock(uniqueListID, header, vehs=None, showFilters=True, showInHangarCB=False, showNotInHangarCB=False, isShowInHangarCBChecked=False, disableChecker=None):
    props = caches.addVehiclesData(uniqueListID, vehs, disableChecker=disableChecker, checkbox=isShowInHangarCBChecked)
    if props.checkbox is not None:
        isShowInHangarCBChecked = props.checkbox
    return UiElement({'linkage': 'VehiclesSortingBlock_UI',
     'hasHeader': showFilters,
     'showNotInHangarCB': showNotInHangarCB,
     'showInHangarCB': showInHangarCB,
     'cbSelected': isShowInHangarCBChecked,
     'vehicles': packVehiclesList(vehs or [], disableChecker),
     'tableHeader': header,
     'nationFilterData': packNationsFilter(),
     'tankFilterData': packIntVehicleTypesFilter(),
     'levelFilterData': packVehicleLevelsFilter(),
     'selectedNation': props.nationIdx,
     'selectedVehType': props.vehTypeIdx,
     'selectedLvl': props.levelIdx,
     'selectedBtnID': props.selectedBtn,
     'sortDirection': props.sortDirect,
     'tableID': uniqueListID})


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


def packIconAwardBonusBlock(awards):
    blockData = {'linkage': 'QuestIconAwardsBlockUI',
     'awards': awards}
    return UiElement(blockData)


def packTextCondition(label, value=None, relation=None, current=None, total=None, isCompleted=False):
    if current is None or total is None:
        progrBarType = PROGRESS_BAR_TYPE.NONE
    else:
        progrBarType = PROGRESS_BAR_TYPE.SIMPLE
    if value is not None:
        value = formatRelation(value, relation)
    if value is not None:
        label = '%s: %s' % (label, value)
    return UiElement({'linkage': 'TextProgressElement_UI',
     'description': label,
     'progrTooltip': None,
     'progrBarType': progrBarType,
     'currentProgrVal': current,
     'maxProgrVal': total,
     'showDone': isCompleted}, 'description')


def packAchieveElement(achieveRecordID):
    """
    :param achieveRecordID: records unique id from dossiers2/custom/records.py
    :param classMedalRank: optional records value, used to show class achievement to
                           determine correct medal rank and image
    """
    block, achieveName = DB_ID_TO_RECORD[achieveRecordID]
    return _packAchieveElement(i18n.makeString('#achievements:%s' % achieveName), '../maps/icons/achievement/32x32/%s.png' % achieveName, block, achieveName)


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


def packIconTextBlock(label, align='right', iconTexts=None):
    return UiElement({'linkage': 'ConditionElement_UI',
     'conditionType': label,
     'contentAlign': align,
     'iconElements': todict(iconTexts or [])}, 'conditionType')


def packSeparator(label, needAlign=False):
    return UiElement({'linkage': 'ConditionSeparator_UI',
     'text': label,
     'needAlign': needAlign})


def packCustomizations(list):
    return UiElement({'linkage': 'CustomizationsBlock_UI',
     'list': list})


def packConditionsBlock(battlesCount=None, counterValue=None, inrow=False, conditions=None, counterDescr=None):
    label = ''
    if battlesCount is not None:
        if inrow:
            labelKey = '#quests:details/conditions/battlesInRow'
        else:
            labelKey = '#quests:details/conditions/battles'
        label = i18n.makeString(labelKey, BigWorld.wg_getIntegralFormat(battlesCount))
    return _packConditionsBlock(label, counterValue, conditions, counterDescr=counterDescr)


def packGroupByVehicleConditions(vehicle, counterValue=None, inrow=False, conditions=None, isCompleted=False, counterDescr=None):
    return _packGroupByConditionsBlock('', vehicle, counterValue, conditions, isCompleted=isCompleted, counterDescr=counterDescr)


def packGroupByLevelConditions(level, counterValue=None, inrow=False, conditions=None, isCompleted=False, counterDescr=None):
    return _packGroupByConditionsBlock(i18n.makeString('#quests:details/conditions/groupBy/levelLabel', int2roman(level)), counterValue=counterValue, conditions=conditions, isCompleted=isCompleted, counterDescr=counterDescr)


def packGroupByNationConditions(nationName, counterValue=None, inrow=False, conditions=None, isCompleted=False, counterDescr=None):
    return _packGroupByConditionsBlock(i18n.makeString('#menu:nations/%s' % nationName), counterValue=counterValue, conditions=conditions, icon='../maps/icons/filters/nations/%s.png' % nationName, isCompleted=isCompleted, counterDescr=counterDescr)


def packGroupByClassConditions(className, counterValue=None, inrow=False, conditions=None, isCompleted=False, counterDescr=None):
    return _packGroupByConditionsBlock(i18n.makeString('#quests:classes/%s' % className), counterValue=counterValue, conditions=conditions, icon='../maps/icons/filters/tanks/%s.png' % className, isCompleted=isCompleted, counterDescr=counterDescr)


def getPQFullDescription(quest):
    return '%s\n%s' % (quest.getUserMainCondition(), quest.getUserAddCondition())


def getFullSeasonUserName(season):
    return i18n.makeString(QUESTS.PERSONAL_SEASONS_ITEMTITLE, num=season.getID(), name=season.getUserName())


def getShortSeasonUserName(season):
    return i18n.makeString('#quests:personal/seasons/shortSeasonName', num=season.getID())


def getFullTileUserName(season, tile):
    return '%s, %s' % (getShortSeasonUserName(season), tile.getUserName())


ProgressData = namedtuple('ProgressData', 'rendererLinkage, progressList')

def packProgressData(rendererLinkage, progressList):
    return ProgressData(rendererLinkage, progressList)


PreFormattedCondition = namedtuple('PreForamttedCondition', 'titleData, descrData, iconKey, current, total, progressData, conditionData, progressType')

def packMissionIconCondition(titleData, progressType, descrData, iconKey, current=None, total=None, progressData=None, conditionData=None):
    return PreFormattedCondition(titleData, descrData, iconKey, current, total, progressData, conditionData, progressType)


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
        return i18n.makeString('#quests:details/conditions/%s/title' % titleKey)
    else:
        return i18n.makeString(QUESTS.DETAILS_CONDITIONS_TARGET_TITLE)
        return


def titleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return text_styles.promoSubTitle(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def titleComplexRelationFormat(value, relation, titleKey=None):
    return titleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey) + icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 8, -4)


def minimizedTitleRelationFormat(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT, titleKey=None):
    return text_styles.stats(_titleRelationFormat(value, relation, relationI18nType, titleKey))


def minimizedTitleComplexRelationFormat(value, relation, titleKey=None):
    return minimizedTitleRelationFormat(value, relation, RELATIONS_SCHEME.DEFAULT, titleKey) + icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_ON, 16, 16, 2, -4)


def titleCumulativeFormat(current, total):
    return text_styles.promoSubTitle('%s / %s' % (BigWorld.wg_getNiceNumberFormat(int(current)), BigWorld.wg_getNiceNumberFormat(int(total))))


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
