# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/vo_converters.py
import BigWorld
from constants import VEHICLE_CLASS_INDICES, VEHICLE_CLASSES
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS, SLOT_LABEL
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.prb_control.settings import UNIT_GUI_ERROR, UNIT_MIN_RECOMMENDED_LEVEL
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES, Vehicle
from helpers import i18n
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter
from nations import INDICES as NATIONS_INDICES, NAMES as NATIONS_NAMES

def getPlayerStatus(slotState, pInfo):
    status = PLAYER_GUI_STATUS.NORMAL
    if slotState.isClosed:
        status = PLAYER_GUI_STATUS.LOCKED
    elif pInfo is not None:
        if pInfo.isCreator():
            status = PLAYER_GUI_STATUS.BATTLE if pInfo.isInArena() else PLAYER_GUI_STATUS.CREATOR
        elif pInfo.isInArena():
            status = PLAYER_GUI_STATUS.BATTLE
        elif pInfo.isReady:
            status = PLAYER_GUI_STATUS.READY
    return status


def makeSlotLabel(unitState, slotState, isCreator = False, vehCount = 0):
    slotLabel = SLOT_LABEL.DEFAULT
    if slotState.isFree:
        if unitState.isLocked():
            template = SLOT_LABEL.LOCKED
        elif not isCreator and vehCount == 0:
            template = SLOT_LABEL.NOT_AVAILABLE
        else:
            template = SLOT_LABEL.EMPTY
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', template)
    elif slotState.isClosed:
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', SLOT_LABEL.CLOSED)
    return slotLabel


def makeVehicleVO(vehicle, maxLevel = 10):
    if vehicle is None:
        return
    else:
        vState, vStateLvl = vehicle.getState()
        isReadyToFight = vehicle.isReadyToFight
        if vState == Vehicle.VEHICLE_STATE.UNDAMAGED or vState == Vehicle.VEHICLE_STATE.IN_PREBATTLE and vehicle.isInUnit:
            vState = ''
            isReadyToFight = True
        else:
            vState = i18n.makeString(MENU.tankcarousel_vehiclestates(vState))
        enabled, tooltip = True, None
        if vehicle.level > maxLevel:
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
        chatRoster = user.getRoster()
    else:
        chatRoster = 0
        colors = colorGetter(USER_GUI_TYPE.OTHER)
    return {'isInvite': pInfo.isInvite(),
     'himself': pInfo.isCurrentPlayer(),
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
     'chatRoster': chatRoster,
     'isPlayerSpeaking': isPlayerSpeaking,
     'isOffline': pInfo.isOffline(),
     'igrType': pInfo.igrType,
     'isRatingAvailable': not pInfo.isInvite()}


def makeSortiePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking = False):
    sortiePlayerVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    sortiePlayerVO['clanAbbrev'] = None
    sortiePlayerVO['isRatingAvailable'] = False
    return sortiePlayerVO


def makeTotalLevelLabel(unitStats):
    hasError = False
    if unitStats.curTotalLevel > unitStats.maxTotalLevel:
        label = makeHtmlString('html_templates:lobby/cyberSport/unit', 'levelError', {'sumLevels': unitStats.curTotalLevel})
        hasError = True
    elif not unitStats.curTotalLevel:
        label = makeHtmlString('html_templates:lobby/cyberSport/unit', 'sumLevelLabel', {'sumLevels': unitStats.curTotalLevel})
    elif unitStats.curTotalLevel < UNIT_MIN_RECOMMENDED_LEVEL:
        label = makeHtmlString('html_templates:lobby/cyberSport/unit', 'levelWarning', {'sumLevels': unitStats.curTotalLevel})
    else:
        label = makeHtmlString('html_templates:lobby/cyberSport/unit', 'levelOk', {'sumLevels': unitStats.curTotalLevel})
    return (hasError, label)


def makeUnitStateLabel(unitState):
    return makeHtmlString('html_templates:lobby/cyberSport', 'teamUnlocked' if unitState.isOpened() else 'teamLocked', {})


def _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app = None, inSearch = False):
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
    if unitState.isSortie():
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
                    vehicleVO = makeVehicleVO(vehicleGetter(vehicle['vehTypeCompDescr']))
        slotLabel = makeSlotLabel(unitState, slotState, isPlayerCreator, vehCount)
        playerStatus = getPlayerStatus(slotState, player)
        restrictions = makeUnitRosterVO(unit, pInfo, index=index)['conditions']
        slot = {'rallyIdx': unitIdx,
         'isCommanderState': isPlayerCreator,
         'isCurrentUserInSlot': isPlayerInSlot,
         'playerStatus': playerStatus,
         'isClosed': slotState.isClosed,
         'isFreezed': unitState.isLocked(),
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
        slots = _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app)
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
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, True),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeSortieShortVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        division = getDivisionNameByType(unit.getRosterTypeID())
        divisionTypeStr = i18n.makeString(FORTIFICATIONS.sortie_division_name(division))
        unit, unitState, _, pInfo, slotsIter = fullData
        return {'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, True),
         'description': divisionTypeStr if divisionTypeStr else unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeSimpleClanListRenderVO(member, intTotalMining, intWeekMining, role):
    week = BigWorld.wg_getIntegralFormat(intWeekMining)
    week = fort_text.getText(fort_text.PURPLE_TEXT, week)
    allTime = BigWorld.wg_getIntegralFormat(intTotalMining)
    allTime = fort_text.getText(fort_text.PURPLE_TEXT, allTime)
    databaseID = member.getID()
    return {'dbID': databaseID,
     'uid': databaseID,
     'himself': bool(BigWorld.player().databaseID == databaseID),
     'userName': member.getName(),
     'playerRole': role,
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
        sumLevelsError, sumLevelsStr = makeTotalLevelLabel(unitStats)
        return {'isCommander': isPlayerCreator,
         'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'statusLbl': makeUnitStateLabel(unitState),
         'statusValue': unitState.isOpened(),
         'sumLevelsInt': unitStats.curTotalLevel,
         'sumLevels': sumLevelsStr,
         'sumLevelsError': sumLevelsError,
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app),
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
        divisionLbl = fort_text.concatStyles(((fort_text.STANDARD_TEXT, divisionStr), (fort_text.MAIN_TEXT, divisionTypeStr)))
        isPlayerCreator = pInfo.isCreator()
        sumLevelsError, sumLevelsStr = makeTotalLevelLabel(unitStats)
        return {'isCommander': isPlayerCreator,
         'isFreezed': unitState.isLocked(),
         'hasRestrictions': unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
         'statusLbl': makeUnitStateLabel(unitState),
         'statusValue': unitState.isOpened(),
         'sumLevelsInt': unitStats.curTotalLevel,
         'sumLevels': sumLevelsStr,
         'sumLevelsError': sumLevelsError,
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx),
         'divisionLbl': divisionLbl}


def makeUnitRosterVO(unit, pInfo, index = None):
    vehicleGetter = g_itemsCache.items.getItemByCD
    if index is None:
        vehiclesData = pInfo.getVehiclesToSlots().keys()
        conditions = [None, None]
    else:
        slots = unit.getRoster().slots
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
                conditions.append({'vehicle': makeVehicleVO(vehicleGetter(vehTypeCD))})
            else:
                params = {'nationIDRange': tuple(),
                 'vTypeRange': tuple(),
                 'vLevelRange': tuple()}
                isDefault = True
                nationMask = rosterSlot.nationMask
                if nationMask != 255:
                    params['nationIDRange'] = filter(lambda k: 1 << NATIONS_INDICES[k] & nationMask, NATIONS_NAMES)
                    isDefault = False
                vehClassMask = rosterSlot.vehClassMask
                if vehClassMask != 255:
                    params['vTypeRange'] = filter(lambda k: 1 << VEHICLE_CLASS_INDICES[k] & vehClassMask, VEHICLE_CLASSES)
                    isDefault = False
                levels = rosterSlot.levels
                if levels != (1, 8):
                    params['vLevelRange'] = levels
                    isDefault = False
                if isDefault:
                    conditions.append(None)
                else:
                    conditions.append(params)

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
        result = makeUnitRosterVO(unit, unitFunctional.getPlayerInfo(unitIdx=unitIdx), index=index)
    return result


def makeUnitActionButtonVO(functional):
    if functional.isCreator():
        result = _makeUnitStartBattleButtonVO(functional)
    else:
        result = _makeUnitReadyButtonVO(functional)
    return result


def makeSortieActionButtonVO(functional):
    if functional.isCreator():
        result = _makeSortieStartBattleButtonVO(functional)
    else:
        result = _makeSortieReadyButtonVO(functional)
    return result


def _makeUnitStartBattleButtonVO(functional):
    isEnabled = False
    stateString = ''
    stats = functional.getStats()
    vInfo = functional.getVehicleInfo()
    if stats.curTotalLevel > stats.maxTotalLevel:
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_LEVELERROR)
    elif vInfo.isEmpty():
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_NOVEHICLE)
    elif not vInfo.isReadyToBattle():
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY)
    elif stats.occupiedSlotsCount <= 1:
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_NOTFULLUNIT)
        isEnabled = stats.occupiedSlotsCount == 1 and not functional.getPlayerInfo().isInArena()
    elif stats.readyCount < stats.occupiedSlotsCount:
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITING)
    elif stats.maxTotalLevel - stats.curTotalLevel < stats.openedSlotsCount - stats.occupiedSlotsCount:
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_LEVELERROR)
    elif stats.readyCount == stats.occupiedSlotsCount:
        isEnabled = not functional.getState().isInIdle() and not functional.getPlayerInfo().isInArena()
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_READY)
    return {'stateString': stateString,
     'label': CYBERSPORT.WINDOW_UNIT_FIGHT,
     'isEnabled': isEnabled}


_unitCandidateErrors = {UNIT_GUI_ERROR.UNIT_IS_FULL: CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE_UNITISFULL,
 UNIT_GUI_ERROR.VEHICLES_NOT_FOUND: CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE_INVALIDVEHICLES,
 UNIT_GUI_ERROR.UNIT_IS_LOCKED: CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE_LOCKEDUNITS}

def _makeSortieStartBattleButtonVO(functional):
    isEnabled = False
    stateString = ''
    stats = functional.getStats()
    vInfo = functional.getVehicleInfo()
    rSettings = functional.getRosterSettings()
    if stats.curTotalLevel > stats.maxTotalLevel:
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_LEVELERROR)
    elif vInfo.isEmpty():
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_NOVEHICLE)
    elif not vInfo.isReadyToBattle():
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_VEHICLEINNOTREADY)
    elif stats.occupiedSlotsCount < rSettings.getMinSlots():
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_NOTFULLUNIT)
        isEnabled = functional.getState().isDevMode() and not functional.getPlayerInfo().isInArena()
    elif stats.readyCount < stats.occupiedSlotsCount:
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_WAITING)
    elif stats.maxTotalLevel - stats.curTotalLevel < stats.openedSlotsCount - stats.occupiedSlotsCount:
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_OPENSLOTS_LEVELERROR)
    elif stats.readyCount == stats.occupiedSlotsCount:
        isEnabled = not functional.getState().isInIdle() and not functional.getPlayerInfo().isInArena()
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_READY)
    return {'stateString': stateString,
     'label': CYBERSPORT.WINDOW_UNIT_FIGHT,
     'isEnabled': isEnabled}


def _makeUnitReadyButtonVO(functional):
    isEnabled = False
    pInfo = functional.getPlayerInfo()
    vInfo = functional.getVehicleInfo()
    if not pInfo.isInSlot:
        canAssign, error = pInfo.canAssignToSlots()
        if not canAssign:
            if error in _unitCandidateErrors:
                stateString = _unitCandidateErrors[error]
            else:
                stateString = ''
                LOG_ERROR('Error message not found', error)
        else:
            stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_CANDIDATE)
    elif vInfo.isEmpty():
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_NOVEHICLE)
    elif not vInfo.isReadyToBattle():
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_VEHICLEINNOTREADY)
    elif pInfo.isReady:
        isEnabled = not functional.getState().isInIdle() and not functional.getPlayerInfo().isInArena()
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_WAITING)
    else:
        isEnabled = not functional.getState().isInIdle() and not functional.getPlayerInfo().isInArena()
        stateString = i18n.makeString(CYBERSPORT.WINDOW_UNIT_MESSAGE_GETREADY)
    if pInfo.isReady:
        label = CYBERSPORT.WINDOW_UNIT_NOTREADY
    else:
        label = CYBERSPORT.WINDOW_UNIT_READY
    return {'stateString': stateString,
     'label': label,
     'isEnabled': isEnabled,
     'isReady': pInfo.isReady}


_sortieCandidateErrors = {UNIT_GUI_ERROR.UNIT_IS_FULL: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE_UNITISFULL,
 UNIT_GUI_ERROR.VEHICLES_NOT_FOUND: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE_INVALIDVEHICLES,
 UNIT_GUI_ERROR.UNIT_IS_LOCKED: FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE_LOCKEDUNITS}

def _makeSortieReadyButtonVO(functional):
    isEnabled = False
    pInfo = functional.getPlayerInfo()
    vInfo = functional.getVehicleInfo()
    if not pInfo.isInSlot:
        canAssign, error = pInfo.canAssignToSlots()
        if not canAssign:
            if error in _sortieCandidateErrors:
                stateString = _sortieCandidateErrors[error]
            else:
                stateString = ''
                LOG_ERROR('Error message not found', error)
        else:
            stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_CANDIDATE)
    elif vInfo.isEmpty():
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_NOVEHICLE)
    elif not vInfo.isReadyToBattle():
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_VEHICLEINNOTREADY)
    elif pInfo.isReady:
        isEnabled = not functional.getState().isInIdle() and not functional.getPlayerInfo().isInArena()
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_WAITING)
    else:
        isEnabled = not functional.getState().isInIdle() and not functional.getPlayerInfo().isInArena()
        stateString = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_MESSAGE_GETREADY)
    if pInfo.isReady:
        label = FORTIFICATIONS.SORTIE_ROOM_NOTREADY
    else:
        label = FORTIFICATIONS.SORTIE_ROOM_READY
    return {'stateString': stateString,
     'label': label,
     'isEnabled': isEnabled,
     'isReady': pInfo.isReady}
