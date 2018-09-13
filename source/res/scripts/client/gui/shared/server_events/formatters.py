# Embedded file name: scripts/client/gui/shared/server_events/formatters.py
import types
from collections import namedtuple
import BigWorld
import constants
import ArenaType
from helpers import i18n, int2roman
from debug_utils import LOG_DEBUG
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui import makeHtmlString, nationCompareByIndex, GUI_NATIONS, getNationIndex
from gui.shared.utils import CONST_CONTAINER
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_TYPES_ORDER_INDICES
from gui.Scaleform.locale.MENU import MENU

class DISCOUNT_TYPE(CONST_CONTAINER):
    PERCENT = 'percent'
    GOLD = 'gold'
    CREDITS = 'credits'
    XP = 'xp'
    FREE_XP = 'freeXp'


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


_g_sortedVehs = {}
VehiclesListProps = namedtuple('VehiclesListProps', ['disableChecker',
 'nationIdx',
 'vehTypeIdx',
 'levelIdx',
 'selectedBtn',
 'sortDirect',
 'checkbox'])

def getVehiclesData(listID):
    return _g_sortedVehs.get(listID)


def addVehiclesData(listID, vehs, disableChecker = None, nationIdx = -1, vehTypeIdx = -1, levelIdx = -1, selectedBtn = None, sortDirect = None, checkbox = None):
    listID = str(listID)
    if listID in _g_sortedVehs:
        _, props = _g_sortedVehs[listID]
    else:
        props = VehiclesListProps(disableChecker, nationIdx, vehTypeIdx, levelIdx, selectedBtn, sortDirect, checkbox)
    _g_sortedVehs[listID] = (vehs, props)
    return props


def updateVehiclesDataProps(listID, **kwargs):
    if listID in _g_sortedVehs:
        vehs, props = _g_sortedVehs[listID]
        _g_sortedVehs[listID] = (vehs, props._replace(**kwargs))


def clearVehiclesData():
    _g_sortedVehs.clear()


class UiElement(object):

    def __init__(self, initDict, labelFieldName = None):
        self._dict = initDict
        self._labelFieldName = labelFieldName
        self._originalLabel = self._dict.get(self._labelFieldName)

    def getDict(self):
        return self._dict

    def getLabel(self):
        if self._labelFieldName is not None:
            return self._dict[self._labelFieldName]
        else:
            return

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


def indexing(uiElements, startIndex = 1, step = 1):
    index = startIndex
    for fmt in uiElements:
        if fmt.setIndex(index):
            index += step

    return uiElements


def _packTableHeaderBtn(btnID, width, label = '', tooltip = '', icon = None):
    return {'id': btnID,
     'label': label,
     'toolTip': tooltip,
     'iconSource': icon,
     'buttonWidth': width}


def _packNationBtn(width):
    return _packTableHeaderBtn('nation', width, label='', icon='../maps/icons/filters/nations/all.png', tooltip='#quests:tooltip/vehTable/nation')


def _packVehTypeBtn(width):
    return _packTableHeaderBtn('type', width, label='', icon='../maps/icons/filters/tanks/all.png', tooltip='#quests:tooltip/vehTable/class')


def _packVehLevelBtn(width):
    return _packTableHeaderBtn('level', width, label='', icon='../maps/icons/buttons/tab_sort_button/level.png', tooltip='#quests:tooltip/vehTable/level')


def _packVehNameBtn(width):
    return _packTableHeaderBtn('vName', width, label='#quests:details/requirements/vehiclesTable/name', tooltip='#quests:tooltip/vehTable/name')


def _packCountBtn(width):
    return _packTableHeaderBtn('count', width, label='#quests:details/requirements/vehiclesTable/count')


def _packUnavailableBtn(width):
    return _packTableHeaderBtn('notAvailable', width, label='', icon='../maps/icons/buttons/tab_sort_button/notAvailable.png', tooltip='#quests:tooltip/vehTable/availability')


def _packDiscountBtn(width):
    return _packTableHeaderBtn('discount', width, label='#quests:details/requirements/vehiclesTable/discount', tooltip='#quests:tooltip/vehTable/discount')


VEH_KILLS_HEADER = VEH_OWNED_HEADER = VEH_UNLOCKS_HEADER = [_packNationBtn(40),
 _packVehTypeBtn(40),
 _packVehLevelBtn(40),
 _packVehNameBtn(254)]
VEH_REQUIRED_HEADER = [_packNationBtn(40),
 _packVehTypeBtn(40),
 _packVehLevelBtn(40),
 _packVehNameBtn(197),
 _packUnavailableBtn(57)]
VEH_ACTION_HEADER = [_packNationBtn(40),
 _packVehTypeBtn(40),
 _packVehLevelBtn(40),
 _packVehNameBtn(154),
 _packDiscountBtn(100)]

def _packVehicleTypesFilter():
    result = [{'label': '#menu:carousel_tank_filter/all',
      'data': -1,
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


def _packVehicle(vehicle, isAvailable = True, discountValue = None, discoutType = None, disableChecker = None, showDone = False):
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


def _packVehiclesList(vehsData, disableChecker):
    result = []
    for v, (isAvailable, discount, discoutType) in vehsData:
        result.append(_packVehicle(v, isAvailable, discount, discoutType, disableChecker))

    return result


def _packIconTextElement(label = '', icon = '', dataType = None, dataValue = None):
    return UiElement({'linkage': 'QuestIconElement_UI',
     'label': label,
     'icon': icon,
     'dataType': dataType,
     'dataValue': dataValue}, 'label')


def _packProgress(current, total, label = ''):
    if current is None or total is None:
        return
    else:
        return {'progrTooltip': None,
         'progrBarType': PROGRESS_BAR_TYPE.SIMPLE,
         'maxProgrVal': total,
         'currentProgrVal': current,
         'description': label}


def _formatRelation(value, relation, relationI18nType = RELATIONS_SCHEME.DEFAULT):
    relation = relation or 'equal'
    if type(value) not in types.StringTypes:
        value = BigWorld.wg_getNiceNumberFormat(value)
    return makeHtmlString('html_templates:lobby/quests', 'relation', {'relation': i18n.makeString('#quests:details/relations%d/%s' % (relationI18nType, relation)),
     'value': value})


def _packConditionsBlock(label, battlesLeft = None, conditions = None, showDone = False):
    return UiElement({'linkage': 'CommonConditionsBlock_UI',
     'description': label,
     'battlesLeft': battlesLeft,
     'progressElements': todict(conditions or []),
     'showDone': showDone}, 'description')


def _packGroupByConditionsBlock(label = '', vehicle = None, battlesLeft = None, conditions = None, icon = None, isCompleted = False):
    return UiElement({'linkage': 'EventProgressBlock_UI',
     'vehicleData': _packVehicle(vehicle),
     'iconSource': icon,
     'description': label,
     'battlesLeft': battlesLeft,
     'progressElements': todict(conditions or []),
     'showDone': isCompleted}, 'description')


_SORTINGS = {'nation': lambda (veh1, _), (veh2, __): nationCompareByIndex(veh1.nationID, veh2.nationID),
 'type': lambda (veh1, _), (veh2, __): veh1._sortByType(veh2),
 'level': lambda (veh1, _), (veh2, __): veh1.level - veh2.level,
 'vName': lambda (veh1, _), (veh2, __): cmp(veh1.userName, veh2.userName),
 'notAvailable': lambda (_, vData1), (__, vData2): cmp(vData1[0], vData2[0]),
 'discount': lambda (_, vData1), (__, vData2): cmp(vData1[1], vData2[1])}

def sortingVehTable(tableID, btnID, direction, nation = None, vehType = None, level = None, cbSelected = None, isAction = None):
    result = []
    vehData = getVehiclesData(tableID)
    if vehData is None:
        return result
    else:
        vehList, props = vehData
        updateVehiclesDataProps(tableID, nationIdx=nation, vehTypeIdx=vehType, levelIdx=level, selectedBtn=btnID, sortDirect=direction, checkbox=cbSelected)
        for v, data in vehList:
            if nation != -1 and getNationIndex(nation) != v.nationID:
                continue
            if vehType != -1 and vehType != VEHICLE_TYPES_ORDER_INDICES[v.type]:
                continue
            if level != -1 and level != v.level:
                continue
            if isAction and cbSelected and v.isInInventory:
                continue
            if not isAction and cbSelected and not v.isInInventory:
                continue
            result.append((v, data))

        if btnID in _SORTINGS:
            result.sort(cmp=_SORTINGS[btnID], reverse=direction == 'descending')
        return _packVehiclesList(result, props.disableChecker)


def makeUniquePath(path, name):
    return '%s.%s' % (path, name)


def makeUniqueTableID(event, uniqueName):
    eventID = ''
    if event is not None:
        eventID = event.getID()
    return makeUniquePath(eventID, uniqueName)


def formatDiscount(discountVal, discountType):
    multiplier = '+' if discountVal < 0 else ''
    if discountType == DISCOUNT_TYPE.GOLD:
        return makeHtmlString('html_templates:lobby/quests/actions', 'gold', {'value': multiplier + BigWorld.wg_getGoldFormat(abs(long(discountVal)))})
    return makeHtmlString('html_templates:lobby/quests/actions', discountType, {'value': multiplier + BigWorld.wg_getIntegralFormat(abs(int(discountVal)))})


def formatGray(msg):
    return makeHtmlString('html_templates:lobby/quests', 'grayTemplate', {'msg': i18n.makeString(msg)})


def formatBright(msg):
    return makeHtmlString('html_templates:lobby/quests', 'brightTemplate', {'msg': i18n.makeString(msg)})


def formatYellow(msg):
    return makeHtmlString('html_templates:lobby/quests', 'yellowTemplate', {'msg': i18n.makeString(msg)})


def formatIndex(index, msg):
    return makeHtmlString('html_templates:lobby/quests', 'index', {'index': index,
     'label': msg})


def packVehicleData(v, discountVal = None, discountType = None):
    discountFmt = None
    if discountVal is not None and discountType is not None:
        discountFmt = formatDiscount(discountVal, discountType)
    return {'nationID': v.nationID,
     'vIconSmall': v.iconSmall,
     'vType': v.type,
     'vLevel': v.level,
     'vName': v.shortUserName,
     'discount': discountFmt}


def packDiscount(label, value = None, discountType = None):
    discountFmt = None
    if value is not None:
        discountFmt = formatDiscount(value, discountType)
    return packTextBlock(label, value=discountFmt)


def getNationName(nation):
    raise nation is not None or AssertionError('nation must be specified')
    return i18n.makeString(MENU.nations(nation))


def packTopLevelContainer(title = '', note = '', subBlocks = None, isOpened = True, isResizable = False, current = None, total = None, showDone = False):
    return UiElement({'linkage': 'ResizableContent_UI',
     'headerTitle': title,
     'headerHtmlPart': note,
     'headerProgress': _packProgress(current, total),
     'containerElements': todict(subBlocks or []),
     'isOpened': isOpened,
     'isResizable': isResizable,
     'showDone': showDone})


def packContainer(title = '', subBlocks = None, isOpened = True, isResizable = False, current = None, total = None, value = None, relation = None, showDone = False):
    if value is not None:
        title = '%s: %s' % (title, _formatRelation(value, relation))
    return UiElement({'linkage': 'InnerResizableContent_UI',
     'headerHtmlPart': title,
     'headerProgress': _packProgress(current, total),
     'containerElements': todict(subBlocks or []),
     'isOpened': isOpened,
     'isResizable': isResizable,
     'showDone': showDone}, 'headerHtmlPart')


def packVehiclesBlock(uniqueListID, header, vehs = None, showFilters = True, showInHangarCB = False, showNotInHangarCB = False, isShowInHangarCBChecked = False, disableChecker = None):
    props = addVehiclesData(uniqueListID, vehs, disableChecker=disableChecker, checkbox=isShowInHangarCBChecked)
    if props.checkbox is not None:
        isShowInHangarCBChecked = props.checkbox
    return UiElement({'linkage': 'VehiclesSortingBlock_UI',
     'hasHeader': showFilters,
     'showNotInHangarCB': showNotInHangarCB,
     'showInHangarCB': showInHangarCB,
     'cbSelected': isShowInHangarCBChecked,
     'vehicles': _packVehiclesList(vehs or [], disableChecker),
     'headerElements': header,
     'nationFilterData': _packNationsFilter(),
     'tankFilterData': _packVehicleTypesFilter(),
     'levelFilterData': _packVehicleLevelsFilter(),
     'selectedNation': props.nationIdx,
     'selectedVehType': props.vehTypeIdx,
     'selectedLvl': props.levelIdx,
     'selectedBtnID': props.selectedBtn,
     'sortDirection': props.sortDirect,
     'tableID': uniqueListID})


def packTextBlock(label, value = None, relation = None, questID = None, isAvailable = True, battlesLeft = 0, showDone = False, relationI18nType = RELATIONS_SCHEME.DEFAULT):
    if value is not None:
        value = _formatRelation(value, relation, relationI18nType)
    raise not (not isAvailable and showDone) or AssertionError
    blockData = {'linkage': 'CounterTextElement_UI',
     'label': label,
     'value': value,
     'linkID': questID,
     'isNotAvailable': not isAvailable,
     'battlesLeft': battlesLeft,
     'showDone': showDone}
    return UiElement(blockData, 'label')


def packTextCondition(label, value = None, relation = None, current = None, total = None, isCompleted = False):
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


def packBonusTypeElement(bonusType):
    return _packIconTextElement(label=i18n.makeString('#menu:bonusType/%d' % bonusType), icon='../maps/icons/battleTypes/%d.png' % bonusType)


def packFormationElement(formationName):
    return _packIconTextElement(label=i18n.makeString('#quests:details/conditions/formation/%s' % formationName), icon='../maps/icons/formation/%s.png' % formationName)


def packHistoricalBattleElement(battleID):
    from gui.shared import g_eventsCache
    battles = g_eventsCache.getHistoricalBattles()
    if battleID in battles:
        battleName = battles[battleID].getUserName()
    else:
        battleName = str(battleID)
    return _packIconTextElement(label=battleName)


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


def packIconTextBlock(label, align = 'right', iconTexts = None):
    return UiElement({'linkage': 'ConditionElement_UI',
     'conditionType': label,
     'contentAlign': align,
     'iconElements': todict(iconTexts or [])}, 'conditionType')


def packSeparator(label, needAlign = False):
    return UiElement({'linkage': 'ConditionSeparator_UI',
     'text': label,
     'needAlign': needAlign})


def packConditionsBlock(battlesCount = None, battlesLeft = None, inrow = False, conditions = None):
    label = ''
    if battlesCount is not None:
        if inrow:
            labelKey = '#quests:details/conditions/battlesInRow'
        else:
            labelKey = '#quests:details/conditions/battles'
        label = i18n.makeString(labelKey, BigWorld.wg_getIntegralFormat(battlesCount))
    return _packConditionsBlock(label, battlesLeft, conditions)


def packGroupByVehicleConditions(vehicle, battlesLeft = None, inrow = False, conditions = None, isCompleted = False):
    return _packGroupByConditionsBlock('', vehicle, battlesLeft, conditions, isCompleted=isCompleted)


def packGroupByLevelConditions(level, battlesLeft = None, inrow = False, conditions = None, isCompleted = False):
    return _packGroupByConditionsBlock(i18n.makeString('#quests:details/conditions/groupBy/levelLabel', int2roman(level)), battlesLeft=battlesLeft, conditions=conditions, isCompleted=isCompleted)


def packGroupByNationConditions(nationName, battlesLeft = None, inrow = False, conditions = None, isCompleted = False):
    return _packGroupByConditionsBlock(i18n.makeString('#menu:nations/%s' % nationName), battlesLeft=battlesLeft, conditions=conditions, icon='../maps/icons/filters/nations/%s.png' % nationName, isCompleted=isCompleted)


def packGroupByClassConditions(className, battlesLeft = None, inrow = False, conditions = None, isCompleted = False):
    return _packGroupByConditionsBlock(i18n.makeString('#quests:classes/%s' % className), battlesLeft=battlesLeft, conditions=conditions, icon='../maps/icons/filters/tanks/%s.png' % className, isCompleted=isCompleted)
