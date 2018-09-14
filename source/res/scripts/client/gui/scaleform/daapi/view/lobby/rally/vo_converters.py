# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/vo_converters.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from constants import VEHICLE_CLASS_INDICES, VEHICLE_CLASSES
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons, TextManager
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS, SLOT_LABEL
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES as FORT_ALIAS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.MENU import MENU
from prebattle_shared import decodeRoster
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES, Vehicle
from helpers import i18n
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter
from nations import INDICES as NATIONS_INDICES, NAMES as NATIONS_NAMES

def getPlayerStatus(slotState, pInfo, autoReadyCreator = False):
    status = PLAYER_GUI_STATUS.NORMAL
    if slotState.isClosed:
        status = PLAYER_GUI_STATUS.LOCKED
    elif pInfo is not None:
        if pInfo.isInArena() or pInfo.isInSearch() or pInfo.isInQueue():
            status = PLAYER_GUI_STATUS.BATTLE
        elif pInfo.isReady:
            status = PLAYER_GUI_STATUS.READY
    return status


def makeSlotLabel(unitState, slotState, isCreator = False, vehCount = 0, checkForVehicles = True):
    slotLabel = SLOT_LABEL.DEFAULT
    if slotState.isFree:
        if unitState.isLocked():
            template = SLOT_LABEL.LOCKED
        elif not isCreator and checkForVehicles and vehCount == 0:
            template = SLOT_LABEL.NOT_AVAILABLE
        else:
            template = SLOT_LABEL.EMPTY
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', template)
    elif slotState.isClosed:
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', SLOT_LABEL.CLOSED)
    return slotLabel


def makeVehicleVO(vehicle, levelsRange = None):
    if vehicle is None:
        return
    else:
        vState, vStateLvl = vehicle.getState()
        isReadyToFight = vehicle.isReadyToFight
        if vState == Vehicle.VEHICLE_STATE.UNDAMAGED or vState == Vehicle.VEHICLE_STATE.IN_PREBATTLE:
            vState = ''
            isReadyToFight = True
        elif vState == Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY:
            vState = makeHtmlString('html_templates:lobby', 'inPremiumIgrOnly')
        else:
            vState = i18n.makeString(MENU.tankcarousel_vehiclestates(vState))
        enabled, tooltip = True, None
        if levelsRange is not None and vehicle.level not in levelsRange:
            enabled, tooltip = False, TOOLTIPS.VEHICLESELECTOR_OVERFLOWLEVEL
        elif vehicle.isOnlyForEventBattles:
            enabled, tooltip = False, '#tooltips:redButton/disabled/vehicle/not_supported'
        return {'intCD': vehicle.intCD,
         'nationID': vehicle.nationID,
         'name': vehicle.name,
         'userName': vehicle.userName,
         'shortUserName': vehicle.shortUserName,
         'level': vehicle.level,
         'type': vehicle.type,
         'typeIndex': VEHICLE_TABLE_TYPES_ORDER_INDICES[vehicle.type],
         'smallIconPath': '../maps/icons/vehicle/small/{0}.png'.format(vehicle.name.replace(':', '-')),
         'isReadyToFight': isReadyToFight,
         'enabled': enabled,
         'tooltip': tooltip,
         'state': vState}


def makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking = False):
    if user is not None:
        colors = colorGetter(user.getGuiType())
        tags = list(user.getTags())
    else:
        colors = colorGetter(USER_GUI_TYPE.OTHER)
        tags = []
    return {'isInvite': pInfo.isInvite(),
     'dbID': pInfo.dbID,
     'accID': pInfo.accID,
     'isCommander': pInfo.isCreator(),
     'userName': pInfo.name,
     'fullName': pInfo.getFullName(),
     'clanAbbrev': pInfo.clanAbbrev,
     'region': pInfo.getRegion(),
     'colors': colors,
     'rating': BigWorld.wg_getIntegralFormat(pInfo.rating),
     'readyState': pInfo.isReady,
     'tags': tags,
     'isPlayerSpeaking': isPlayerSpeaking,
     'isOffline': pInfo.isOffline(),
     'igrType': pInfo.igrType,
     'isRatingAvailable': not pInfo.isInvite()}


def makeSortiePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking = False):
    sortiePlayerVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    sortiePlayerVO['isLegionaries'] = pInfo.isLegionary()
    sortiePlayerVO['clanAbbrev'] = None
    sortiePlayerVO['isRatingAvailable'] = pInfo.isLegionary()
    return sortiePlayerVO


def makeClanBattlePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking = False):
    sortiePlayerVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    sortiePlayerVO['clanAbbrev'] = None
    sortiePlayerVO['isRatingAvailable'] = False
    return sortiePlayerVO


_UNIT_RESTRICTION_TO_LABEL = {UNIT_RESTRICTION.MAX_TOTAL_LEVEL: 'levelError',
 UNIT_RESTRICTION.MIN_TOTAL_LEVEL: 'levelError',
 UNIT_RESTRICTION.INVALID_TOTAL_LEVEL: 'levelWarning'}

def makeTotalLevelLabel(unitStats, restriction = ''):
    templateKey = 'sumLevelLabel'
    if restriction:
        if restriction in _UNIT_RESTRICTION_TO_LABEL:
            templateKey = _UNIT_RESTRICTION_TO_LABEL[restriction]
    else:
        templateKey = 'levelOk'
    label = makeHtmlString('html_templates:lobby/cyberSport/unit', templateKey, {'sumLevels': unitStats.curTotalLevel})
    return label


def makeUnitStateLabel(unitState):
    return makeHtmlString('html_templates:lobby/cyberSport', 'teamUnlocked' if unitState.isOpened() else 'teamLocked', {})


def _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app = None, levelsRange = None, checkForVehicles = True):
    isPlayerCreator = pInfo.isCreator()
    isPlayerInSlot = pInfo.isInSlot
    slots = []
    userGetter = storage_getter('users')().getUser
    colorGetter = g_settings.getColorScheme('rosters').getColors
    vehicleGetter = g_itemsCache.items.getItemByCD
    if app:
        isPlayerSpeaking = app.voiceChatManager.isPlayerSpeaking
    else:
        isPlayerSpeaking = lambda dbID: False
    if unitState.isFortBattle():
        makeVO = makeClanBattlePlayerVO
    elif unitState.isSortie():
        makeVO = makeSortiePlayerVO
    else:
        makeVO = makePlayerVO
    for slotInfo in slotsIter:
        index = slotInfo.index
        slotState = slotInfo.state
        player = slotInfo.player
        vehicle = slotInfo.vehicle
        canAssign, vehicles = pInfo.canAssignToSlot(index)
        vehCount = len(vehicles)
        slotLevel = 0
        vehicleVO = None
        slotPlayerUI = None
        if player is not None:
            dbID = player.dbID
            slotPlayerUI = makeVO(player, userGetter(dbID), colorGetter, isPlayerSpeaking(dbID))
            if vehicle:
                if 'vehLevel' in vehicle:
                    slotLevel = vehicle['vehLevel']
                if 'vehTypeCompDescr' in vehicle:
                    vehicleVO = makeVehicleVO(vehicleGetter(vehicle['vehTypeCompDescr']), levelsRange)
        slotLabel = makeSlotLabel(unitState, slotState, isPlayerCreator, vehCount, checkForVehicles)
        playerStatus = getPlayerStatus(slotState, player, unitState.isFortBattle())
        if unit is not None:
            restrictions = makeUnitRosterVO(unit, pInfo, index=index, isSortie=unitState.isSortie(), levelsRange=levelsRange)['conditions']
        else:
            restrictions = []
        isFreezed = unitState.isLocked() or unitState.isInSearch() or unitState.isInQueue() or unitState.isInArena()
        slot = {'rallyIdx': unitIdx,
         'isCommanderState': isPlayerCreator,
         'isCurrentUserInSlot': isPlayerInSlot,
         'playerStatus': playerStatus,
         'isClosed': slotState.isClosed,
         'isFreezed': isFreezed,
         'slotLabel': slotLabel,
         'player': slotPlayerUI,
         'canBeTaken': canAssign,
         'compatibleVehiclesCount': vehCount,
         'selectedVehicle': vehicleVO,
         'selectedVehicleLevel': 1 if slotState.isClosed else slotLevel,
         'restrictions': restrictions}
        slots.append(slot)

    return slots


def makeSlotsVOs(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        slots = _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange())
        isRosterSet = unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES)
        return (isRosterSet, slots)


def getUnitMaxLevel(unitFunctional, unitIdx = None, app = None):
    level = 10
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is not None:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        division = getDivisionNameByType(unit.getRosterTypeID())
        level = getDivisionLevel(division)
    return level


def makeUnitShortVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, _, pInfo, slotsIter = fullData
        return {'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange()),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeSortieShortVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        textMgr = TextManager.reference()
        title = i18n.makeString(FORTIFICATIONS.SORTIE_LISTVIEW_ALERTTEXT_TITLE)
        body = i18n.makeString(FORTIFICATIONS.SORTIE_LISTVIEW_ALERTTEXT_BODY)
        alertView = {'icon': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON,
         'titleMsg': textMgr.getText(TextType.ALERT_TEXT, title),
         'bodyMsg': textMgr.getText(TextType.MAIN_TEXT, body),
         'buttonLbl': FORTIFICATIONS.SORTIE_LISTVIEW_ENTERBTN}
        return {'isShowAlertView': True,
         'alertView': alertView}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        division = getDivisionNameByType(unit.getRosterTypeID())
        divisionTypeStr = i18n.makeString(FORTIFICATIONS.sortie_division_name(division))
        unit, unitState, _, pInfo, slotsIter = fullData
        return {'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange()),
         'description': divisionTypeStr if divisionTypeStr else unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeMsg(value):
    return i18n.makeString(value)


def makeFortBattleShortVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, _, pInfo, slotsIter = fullData
        return {'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange()),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeSimpleClanListRenderVO(member, intTotalMining, intWeekMining, role, roleID):
    week = BigWorld.wg_getIntegralFormat(intWeekMining)
    week = TextManager.reference().getText(TextType.DEFRES_TEXT, week)
    allTime = BigWorld.wg_getIntegralFormat(intTotalMining)
    allTime = TextManager.reference().getText(TextType.DEFRES_TEXT, allTime)
    databaseID = member.getID()
    return {'dbID': databaseID,
     'uid': databaseID,
     'himself': bool(BigWorld.player().databaseID == databaseID),
     'userName': member.getName(),
     'playerRole': role,
     'playerRoleID': roleID,
     'thisWeek': week,
     'allTime': allTime,
     'intWeekMining': intWeekMining,
     'intTotalMining': intTotalMining,
     'fullName': member.getFullName()}


def makeUnitVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        isPlayerCreator = pInfo.isCreator()
        canDoAction, restriction = unitFunctional.validateLevels(stats=unitStats)
        sumLevelsStr = makeTotalLevelLabel(unitStats, restriction)
        return {'isCommander': isPlayerCreator,
         'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'statusLbl': makeUnitStateLabel(unitState),
         'statusValue': unitState.isOpened(),
         'sumLevelsInt': unitStats.curTotalLevel,
         'sumLevels': sumLevelsStr,
         'sumLevelsError': canDoAction,
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange()),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeSortieVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        division = getDivisionNameByType(unit.getRosterTypeID())
        divisionTypeStr = i18n.makeString(FORTIFICATIONS.sortie_division_name(division))
        divisionStr = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_DIVISION)
        divisionLbl = TextManager.reference().concatStyles(((TextType.STANDARD_TEXT, divisionStr), (TextType.MAIN_TEXT, divisionTypeStr)))
        isPlayerCreator = pInfo.isCreator()
        canDoAction, restriction = unitFunctional.validateLevels(stats=unitStats)
        sumLevelsStr = makeTotalLevelLabel(unitStats, restriction)
        return {'isCommander': isPlayerCreator,
         'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'statusLbl': makeUnitStateLabel(unitState),
         'statusValue': unitState.isOpened(),
         'sumLevelsInt': unitStats.curTotalLevel,
         'sumLevels': sumLevelsStr,
         'sumLevelsError': canDoAction,
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange()),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx),
         'divisionLbl': divisionLbl}


def makeFortBattleVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        isPlayerCreator = pInfo.isCreator()
        canDoAction, restriction = unitFunctional.validateLevels(stats=unitStats)
        sumLevelsStr = makeTotalLevelLabel(unitStats, restriction)
        return {'isCommander': isPlayerCreator,
         'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'statusLbl': makeUnitStateLabel(unitState),
         'statusValue': unitState.isOpened(),
         'sumLevelsInt': unitStats.curTotalLevel,
         'sumLevels': sumLevelsStr,
         'sumLevelsError': canDoAction,
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange()),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeSquadVO(squadFunctional, app = None):
    fullData = squadFunctional.getUnitFullData()
    if fullData is None:
        return {}
    else:
        unitState, unitStats, pInfo, slotsIter = fullData
        slotsData = _getSlotsData(-1, None, unitState, pInfo, slotsIter, app, checkForVehicles=False)
        return {'isCommander': squadFunctional.isCreator(),
         'isFreezed': unitState.isLocked(),
         'hasRestrictions': False,
         'statusLbl': makeUnitStateLabel(unitState),
         'statusValue': unitState.isOpened(),
         'sumLevelsInt': unitStats.curTotalLevel,
         'sumLevels': '',
         'sumLevelsError': False,
         'slots': slotsData,
         'description': ''}


def makeUnitRosterVO(unit, pInfo, index = None, isSortie = False, levelsRange = None):
    vehicleGetter = g_itemsCache.items.getItemByCD
    if index is None:
        vehiclesData = pInfo.getVehiclesToSlots().keys()
        conditions = [None, None]
    else:
        slots = unit.getRoster().slots
        isDefaultSlot = unit.getRoster().isDefaultSlot
        rosterSlotConditions = [None, None]
        rosterSlotIdx = index * 2
        if rosterSlotIdx in slots:
            rosterSlotConditions[0] = slots[rosterSlotIdx]
        rosterSlotIdx += 1
        if rosterSlotIdx in slots:
            rosterSlotConditions[1] = slots[rosterSlotIdx]
        conditions = []
        for rosterSlot in rosterSlotConditions:
            if rosterSlot is None:
                conditions.append(None)
                continue
            vehTypeCD = rosterSlot.vehTypeCompDescr
            if vehTypeCD is not None:
                conditions.append({'vehicle': makeVehicleVO(vehicleGetter(vehTypeCD), levelsRange)})
            else:
                params = {'nationIDRange': tuple(),
                 'vTypeRange': tuple(),
                 'vLevelRange': tuple()}
                isDefault = not isSortie and isDefaultSlot(rosterSlot)
                if not isDefault:
                    nationMask = rosterSlot.nationMask
                    if nationMask != 255:
                        params['nationIDRange'] = filter(lambda k: 1 << NATIONS_INDICES[k] & nationMask, NATIONS_NAMES)
                    vehClassMask = rosterSlot.vehClassMask
                    if vehClassMask != 255:
                        params['vTypeRange'] = filter(lambda k: 1 << VEHICLE_CLASS_INDICES[k] & vehClassMask, VEHICLE_CLASSES)
                    levels = rosterSlot.levels
                    if levels != rosterSlot.DEFAULT_LEVELS or isSortie:
                        params['vLevelRange'] = levels
                    conditions.append(params)
                else:
                    conditions.append(None)

        vehiclesData = pInfo.getVehiclesToSlot(index)
    vehicleVOs = map(lambda vehTypeCD: makeVehicleVO(vehicleGetter(vehTypeCD)), vehiclesData)
    return getUnitRosterModel(vehicleVOs, conditions, pInfo.isCreator())


def getUnitRosterModel(vehiclesData, conditions, isCreator):
    return {'vehicles': vehiclesData,
     'conditions': conditions,
     'isCreator': isCreator}


def getUnitRosterData(unitFunctional, unitIdx = None, index = None):
    _, unit = unitFunctional.getUnit(unitIdx)
    if unit is None:
        result = {}
    else:
        result = makeUnitRosterVO(unit, unitFunctional.getPlayerInfo(unitIdx=unitIdx), index=index, isSortie=unitFunctional.getState(unitIdx=unitIdx).isSortie(), levelsRange=unitFunctional.getRosterSettings().getLevelsRange())
    return result


def makeBuildingIndicatorsVOByDescr(buildingDescr):
    buildingLevel = buildingDescr.level
    progress = FORT_ALIAS.STATE_BUILDING if buildingLevel else FORT_ALIAS.STATE_FOUNDATION_DEF
    hpVal = buildingDescr.hp
    hpTotalVal = buildingDescr.levelRef.hp
    defResVal = buildingDescr.storage
    maxDefResVal = buildingDescr.levelRef.storage
    return makeBuildingIndicatorsVO(buildingLevel, progress, hpVal, hpTotalVal, defResVal, maxDefResVal)


def makeBuildingIndicatorsVO(buildingLevel, progress, hpVal, hpTotalVal, defResVal, maxDefResVal):
    textStyle = TextType.DEFRES_TEXT
    if progress == FORT_ALIAS.STATE_FOUNDATION_DEF or progress == FORT_ALIAS.STATE_FOUNDATION:
        textStyle = TextType.ALERT_TEXT
    formattedHpValue = TextManager.reference().getText(textStyle, str(BigWorld.wg_getIntegralFormat(hpVal)))
    hpTotalFormatted = str(BigWorld.wg_getIntegralFormat(hpTotalVal)) + ' '
    formattedHpTotal = TextManager.reference().concatStyles(((TextType.STANDARD_TEXT, hpTotalFormatted), (TextIcons.NUT_ICON,)))
    formattedDefResValue = TextManager.reference().getText(TextType.DEFRES_TEXT, str(BigWorld.wg_getIntegralFormat(defResVal)))
    maxDefDerFormatted = str(BigWorld.wg_getIntegralFormat(maxDefResVal)) + ' '
    formattedDefResTotal = TextManager.reference().concatStyles(((TextType.STANDARD_TEXT, maxDefDerFormatted), (TextIcons.NUT_ICON,)))
    hpProgressLabels = {'currentValue': formattedHpValue,
     'totalValue': formattedHpTotal,
     'separator': '/'}
    storeProgressLabels = {'currentValue': formattedDefResValue,
     'totalValue': formattedDefResTotal,
     'separator': '/'}
    result = {'hpLabel': i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_HPLBL),
     'defResLabel': i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_DEFRESLBL),
     'hpCurrentValue': hpVal,
     'hpTotalValue': hpTotalVal,
     'defResCurrentValue': defResVal,
     'defResTotalValue': maxDefResVal,
     'hpProgressLabels': hpProgressLabels,
     'defResProgressLabels': storeProgressLabels}
    return result


class SquadActionButtonStateVO(dict):

    def __init__(self, prbFunctional):
        super(SquadActionButtonStateVO, self).__init__()
        stateString = ''
        pInfo = prbFunctional.getPlayerInfo()
        team, assigned = decodeRoster(prbFunctional.getRosterKey())
        isInQueue = prbFunctional.getTeamState().isInQueue()
        isEnabled = g_currentVehicle.isReadyToPrebattle() and not (isInQueue and assigned)
        if not g_currentVehicle.isPresent():
            stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_NOVEHICLE)
        elif not g_currentVehicle.isReadyToPrebattle():
            stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY)
        elif not pInfo.isReady():
            stateString = i18n.makeString(MESSENGER.DIALOGS_SQUAD_MESSAGE_GETREADY)
        elif pInfo.isReady() and not isInQueue:
            stateString = i18n.makeString(MESSENGER.DIALOGS_SQUAD_MESSAGE_GETNOTREADY)
        if pInfo.isReady():
            label = CYBERSPORT.WINDOW_UNIT_NOTREADY
        else:
            label = CYBERSPORT.WINDOW_UNIT_READY
        self['stateString'] = stateString
        self['label'] = label
        self['isEnabled'] = isEnabled
        self['isReady'] = pInfo.isReady()
