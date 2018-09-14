# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/formatters.py
import types
import BigWorld
import constants
import ArenaType
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.shared.formatters import text_styles
from helpers import i18n, int2roman
from dossiers2.custom.records import DB_ID_TO_RECORD
from shared_utils import CONST_CONTAINER
from gui import makeHtmlString, GUI_NATIONS
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.server_events import caches
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.QUESTS import QUESTS
from constants import ARENA_BONUS_TYPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class DISCOUNT_TYPE(CONST_CONTAINER):
    PERCENT = 'percent'
    GOLD = 'gold'
    CREDITS = 'credits'
    XP = 'xp'
    FREE_XP = 'freeXp'
    MULTIPLIER = 'multiplier'


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


def _packTableHeaderBtn(btnID, width, label='', tooltip='', icon=None, showSeparator=True):
    return {'id': btnID,
     'label': label,
     'toolTip': tooltip,
     'iconSource': icon,
     'buttonWidth': width,
     'buttonHeight': 40,
     'defaultSortDirection': 'descending',
     'ascendingIconSource': '../maps/icons/buttons/tab_sort_button/ascProfileSortArrow.png',
     'descendingIconSource': '../maps/icons/buttons/tab_sort_button/descProfileSortArrow.png',
     'showSeparator': showSeparator}


def _packNationBtn(width):
    return _packTableHeaderBtn('nation', width, label='', icon='../maps/icons/filters/nations/all.png', tooltip='#quests:tooltip/vehTable/nation')


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

def _packVehicleTypesFilter(defaultVehType=-1):
    result = [{'label': '#menu:carousel_tank_filter/all',
      'data': defaultVehType,
      'icon': '../maps/icons/filters/tanks/none.png'}]
    for idx, vehicleType in enumerate(VEHICLE_TYPES_ORDER):
        result.append({'label': '#menu:carousel_tank_filter/%s' % vehicleType,
         'data': idx,
         'icon': '../maps/icons/filters/tanks/%s.png' % vehicleType})

    return result


def _packNationsFilter():
    result = [{'label': '#menu:nations/all',
      'data': -1,
      'icon': '../maps/icons/filters/nations/all.png'}]
    for idx, nation in enumerate(GUI_NATIONS):
        result.append({'label': '#menu:nations/%s' % nation,
         'data': idx,
         'icon': '../maps/icons/filters/nations/%s.png' % nation})

    return result


def _packVehicleLevelsFilter():
    result = [{'label': '#menu:levels/all',
      'data': -1,
      'icon': '../maps/icons/filters/levels/level_all.png'}]
    for level in xrange(1, constants.MAX_VEHICLE_LEVEL + 1):
        result.append({'label': '#menu:levels/%d' % level,
         'data': level,
         'icon': '../maps/icons/filters/levels/level_%s.png' % level})

    return result


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


def _formatRelation(value, relation, relationI18nType=RELATIONS_SCHEME.DEFAULT):
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
    return makeHtmlString('html_templates:lobby/quests/actions', 'gold', {'value': multiplier + BigWorld.wg_getGoldFormat(abs(long(discountVal)))}) if discountType == DISCOUNT_TYPE.GOLD else makeHtmlString('html_templates:lobby/quests/actions', discountType, {'value': multiplier + BigWorld.wg_getIntegralFormat(abs(int(discountVal)))})


def formatGray(msg):
    return makeHtmlString('html_templates:lobby/quests', 'grayTemplate', {'msg': i18n.makeString(msg)})


def formatBright(msg):
    return makeHtmlString('html_templates:lobby/quests', 'brightTemplate', {'msg': i18n.makeString(msg)})


def formatYellow(msg, *args, **kwargs):
    return makeHtmlString('html_templates:lobby/quests', 'yellowTemplate', {'msg': i18n.makeString(msg, *args, **kwargs)})


def formatIndex(index, msg):
    return makeHtmlString('html_templates:lobby/quests', 'index', {'index': index,
     'label': msg})


def packVehicleData(v, discountVal=None, discountType=None):
    discountFmt = None
    if discountVal is not None and discountType is not None:
        discountFmt = formatDiscount(discountVal, discountType)
    return {'nationID': v.nationID,
     'vIconSmall': v.iconSmall,
     'vType': v.type,
     'vLevel': v.level,
     'vName': v.shortUserName,
     'discount': discountFmt}


def packDiscount(label, value=None, discountType=None):
    discountFmt = None
    if value is not None:
        discountFmt = formatDiscount(value, discountType)
    return packTextBlock(label, value=discountFmt)


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


def packMotiveContainer(title='', note='', subBlocks=None, isOpened=True, isResizable=False, current=None, total=None, showDone=False):
    return UiElement({'linkage': 'ResizableContent_UI',
     'headerTitle': title,
     'headerHtmlPart': note,
     'headerProgress': _packProgress(current, total),
     'containerElements': subBlocks or [],
     'isOpened': isOpened,
     'isResizable': isResizable,
     'showDone': showDone})


def packContainer(title='', subBlocks=None, isOpened=True, isResizable=False, current=None, total=None, value=None, relation=None, showDone=False):
    if value is not None:
        title = '%s: %s' % (title, _formatRelation(value, relation))
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
     'nationFilterData': _packNationsFilter(),
     'tankFilterData': _packVehicleTypesFilter(),
     'levelFilterData': _packVehicleLevelsFilter(),
     'selectedNation': props.nationIdx,
     'selectedVehType': props.vehTypeIdx,
     'selectedLvl': props.levelIdx,
     'selectedBtnID': props.selectedBtn,
     'sortDirection': props.sortDirect,
     'tableID': uniqueListID})


def packTextBlock(label, value=None, relation=None, questID=None, isAvailable=True, fullLabel=None, counterValue=0, showDone=False, relationI18nType=RELATIONS_SCHEME.DEFAULT, counterDescr=None):
    if value is not None:
        value = _formatRelation(value, relation, relationI18nType)
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
        value = _formatRelation(value, relation)
    if value is not None:
        label = '%s: %s' % (label, value)
    return UiElement({'linkage': 'TextProgressElement_UI',
     'description': label,
     'progrTooltip': None,
     'progrBarType': progrBarType,
     'currentProgrVal': current,
     'maxProgrVal': total,
     'showDone': isCompleted}, 'description')


def packBonusTypeElements(bonusTypes):
    uniqueTypes = set()
    for bonusType in bonusTypes:
        if bonusType in (ARENA_BONUS_TYPE.SANDBOX, ARENA_BONUS_TYPE.RATED_SANDBOX):
            bonusType = ARENA_BONUS_TYPE.RATED_SANDBOX
        if bonusType in (ARENA_BONUS_TYPE.TOURNAMENT_REGULAR, ARENA_BONUS_TYPE.TOURNAMENT_CLAN):
            bonusType = ARENA_BONUS_TYPE.TOURNAMENT
        uniqueTypes.add(bonusType)

    elements = []
    for bonusType in uniqueTypes:
        elements.append(_packIconTextElement(label=i18n.makeString('#menu:bonusType/%d' % bonusType), icon='../maps/icons/battleTypes/%d.png' % bonusType))

    return elements


def packFormationElement(formationName):
    return _packIconTextElement(label=i18n.makeString('#quests:details/conditions/formation/%s' % formationName), icon='../maps/icons/formation/%s.png' % formationName)


def packAchieveElement(achieveRecordID):
    block, achieveName = DB_ID_TO_RECORD[achieveRecordID]
    return _packIconTextElement(label=i18n.makeString('#achievements:%s' % achieveName), icon='../maps/icons/achievement/32x32/%s.png' % achieveName, dataType='battleStatsAchievementData', dataValue=[block, achieveName])


def packCamoElement(camoTypeName):
    return _packIconTextElement(label=i18n.makeString('#quests:details/conditions/mapsType/%s' % camoTypeName))


def packMapElement(arenaTypeID):
    if arenaTypeID not in ArenaType.g_cache:
        return None
    else:
        arenaType = ArenaType.g_cache[arenaTypeID]
        if arenaType.gameplayName != 'ctf':
            label = '%s (%s)' % (arenaType.name, i18n.makeString('#arenas:type/%s/name' % arenaType.gameplayName))
        else:
            label = arenaType.name
        return _packIconTextElement(label=label)


def packIconTextBlock(label, align='right', iconTexts=None):
    return UiElement({'linkage': 'ConditionElement_UI',
     'conditionType': label,
     'contentAlign': align,
     'iconElements': todict(iconTexts or [])}, 'conditionType')


def packSeparator(label, needAlign=False):
    return UiElement({'linkage': 'ConditionSeparator_UI',
     'text': label,
     'needAlign': needAlign})


def packQuestDetailsSeparator(leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0):
    return UiElement({'linkage': 'QuestDetailsSeparatorBlockUI',
     'paddings': {'left': leftPadding,
                  'right': rightPadding,
                  'top': topPadding,
                  'bottom': bottomPadding}})


def packQuestDetailsSpacing(spacing=0):
    return UiElement({'linkage': 'QuestDetailsSpacingBlockUI',
     'spacing': spacing})


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


def packGroupBlock(groupName):
    return {'isSelectable': False,
     'rendererType': QUESTS_ALIASES.RENDERER_TYPE_BLOCK_TITLE,
     'description': text_styles.highTitle(groupName)}
