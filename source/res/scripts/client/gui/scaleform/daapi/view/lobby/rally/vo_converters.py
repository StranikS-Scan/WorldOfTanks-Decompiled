# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/vo_converters.py
import BigWorld
from constants import VEHICLE_CLASS_INDICES, VEHICLE_CLASSES, FALLOUT_BATTLE_TYPE
from gui.LobbyContext import g_lobbyContext
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS, SLOT_LABEL
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES as FORT_ALIAS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control import getFalloutCtrl
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES, Vehicle
from helpers import i18n, int2roman
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter
from nations import INDICES as NATIONS_INDICES, NAMES as NATIONS_NAMES
from gui.server_events import g_eventsCache
from gui.shared.utils.functions import makeTooltip
from gui.shared.formatters import icons, text_styles

def getPlayerStatus(slotState, pInfo):
    if slotState.isClosed:
        return PLAYER_GUI_STATUS.LOCKED
    else:
        if pInfo is not None:
            if pInfo.isInArena() or pInfo.isInPreArena() or pInfo.isInSearch() or pInfo.isInQueue():
                return PLAYER_GUI_STATUS.BATTLE
            if pInfo.isReady:
                return PLAYER_GUI_STATUS.READY
        return PLAYER_GUI_STATUS.NORMAL


def getSquadPlayerStatus(slotState, pInfo):
    if slotState.isClosed:
        return PLAYER_GUI_STATUS.LOCKED
    else:
        if pInfo is not None:
            if pInfo.isInArena():
                return PLAYER_GUI_STATUS.BATTLE
            if pInfo.isReady:
                return PLAYER_GUI_STATUS.READY
        return PLAYER_GUI_STATUS.NORMAL


def makeSlotLabel(unitFlags, slotState, isCreator = False, vehCount = 0, checkForVehicles = True, isRequired = False):
    slotLabel = SLOT_LABEL.DEFAULT
    if slotState.isFree:
        if unitFlags.isLocked():
            template = SLOT_LABEL.LOCKED
        elif not isCreator and checkForVehicles and vehCount == 0:
            template = SLOT_LABEL.NOT_AVAILABLE
        elif isCreator and isRequired:
            template = SLOT_LABEL.REQUIRED
        else:
            template = SLOT_LABEL.EMPTY
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', template)
    elif slotState.isClosed:
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', SLOT_LABEL.CLOSED)
    return slotLabel


def makeStaticSlotLabel(unitState, slotState, isCreator = False, vehCount = 0, checkForVehicles = True, isLegionary = False, isRated = False):
    slotLabel = SLOT_LABEL.DEFAULT
    if slotState.isFree:
        if unitState.isLocked():
            template = SLOT_LABEL.LOCKED
        elif not isCreator and checkForVehicles and vehCount == 0:
            template = SLOT_LABEL.NOT_AVAILABLE
        elif isLegionary and isRated:
            template = SLOT_LABEL.NOT_ALLOWED
        else:
            template = SLOT_LABEL.EMPTY
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', template)
    elif slotState.isClosed:
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', SLOT_LABEL.CLOSED)
    return slotLabel


def makeVehicleBasicVO(vehicle, levelsRange = None, vehicleTypes = None):
    if vehicle is None:
        return
    else:
        enabled, tooltip = True, None
        if levelsRange is not None and vehicle.level not in levelsRange:
            enabled, tooltip = False, TOOLTIPS.VEHICLESELECTOR_OVERFLOWLEVEL
        elif vehicleTypes is not None and vehicle.type not in vehicleTypes:
            enabled, tooltip = False, TOOLTIPS.VEHICLESELECTOR_INCOMPATIBLETYPE
        return {'intCD': vehicle.intCD,
         'nationID': vehicle.nationID,
         'name': vehicle.name,
         'userName': vehicle.userName,
         'shortUserName': vehicle.shortUserName,
         'level': vehicle.level,
         'type': vehicle.type,
         'typeIndex': VEHICLE_TABLE_TYPES_ORDER_INDICES[vehicle.type],
         'smallIconPath': '../maps/icons/vehicle/small/{0}.png'.format(vehicle.name.replace(':', '-')),
         'isReadyToFight': True,
         'enabled': enabled,
         'tooltip': tooltip,
         'state': '',
         'isFalloutVehicle': vehicle.isFalloutSelected}


def makeVehicleVO(vehicle, levelsRange = None, vehicleTypes = None, isCurrentPlayer = True):
    vehicleVO = makeVehicleBasicVO(vehicle, levelsRange, vehicleTypes)
    if vehicleVO is None:
        return
    else:
        vState, vStateLvl = vehicle.getState(isCurrentPlayer)
        if not (vState == Vehicle.VEHICLE_STATE.UNDAMAGED or vState == Vehicle.VEHICLE_STATE.IN_PREBATTLE or vState in Vehicle.GROUP_STATES):
            vehicleVO['isReadyToFight'] = vehicle.isReadyToFight
            if vState == Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY:
                vehicleVO['state'] = makeHtmlString('html_templates:lobby', 'inPremiumIgrOnly')
            else:
                vehicleVO['state'] = i18n.makeString('#menu:tankCarousel/vehicleStates/%s' % vState)
        if not vehicleVO['isReadyToFight']:
            vehicleVO['enabled'], vehicleVO['tooltip'] = False, makeTooltip('#tooltips:vehicleStatus/%s/header' % vState, '#tooltips:vehicleStatus/body')
        return vehicleVO


def makeUserVO(user, colorGetter, isPlayerSpeaking = False):
    if user is not None:
        colors = colorGetter(user.getGuiType())
        tags = list(user.getTags())
    else:
        colors = colorGetter(USER_GUI_TYPE.OTHER)
        tags = []
    return {'isInvite': False,
     'dbID': user.getID(),
     'accID': -1,
     'isCommander': True,
     'userName': user.getName(),
     'fullName': user.getFullName(),
     'clanAbbrev': user.getClanAbbrev(),
     'region': g_lobbyContext.getRegionCode(user.getID()),
     'colors': colors,
     'rating': None,
     'readyState': False,
     'tags': tags,
     'isPlayerSpeaking': isPlayerSpeaking,
     'isOffline': not user.isOnline(),
     'igrType': 0,
     'isRatingAvailable': True}


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


def makeStaticFormationPlayerVO(pInfo, user, colorGetter, isPlayerSpeaking = False):
    staticFormationPlayerVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    staticFormationPlayerVO['isLegionaries'] = pInfo.isLegionary()
    staticFormationPlayerVO['isRatingAvailable'] = pInfo.isLegionary() and not pInfo.isInSlot
    return staticFormationPlayerVO


def makeClanBattlePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking = False):
    clanBattleVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    clanBattleVO['clanAbbrev'] = None
    clanBattleVO['isRatingAvailable'] = False
    return clanBattleVO


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
    canTakeSlot = not pInfo.isLegionary()
    if app:
        isPlayerSpeaking = app.voiceChatManager.isPlayerSpeaking
    else:
        isPlayerSpeaking = lambda dbID: False
    if unit.isSquad():
        falloutBattleType = unit.getExtra().eventType
        isFallout = falloutBattleType != FALLOUT_BATTLE_TYPE.UNDEFINED
        falloutCfg = g_eventsCache.getFalloutConfig(falloutBattleType)
    else:
        falloutBattleType = FALLOUT_BATTLE_TYPE.UNDEFINED
        isFallout = False
        falloutCfg = None
    if unit is None:
        makeVO = makePlayerVO
    elif unit.isFortBattle():
        makeVO = makeClanBattlePlayerVO
    elif unit.isSortie():
        makeVO = makeSortiePlayerVO
    elif unit.isClub():
        makeVO = makeStaticFormationPlayerVO
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
            isCurrentPlayer = player.isCurrentPlayer()
            if vehicle:
                if 'vehLevel' in vehicle:
                    slotLevel = vehicle['vehLevel']
                if 'vehTypeCompDescr' in vehicle:
                    vehicleVO = makeVehicleVO(vehicleGetter(vehicle['vehTypeCompDescr']), levelsRange, isCurrentPlayer=isCurrentPlayer)
        if unit is not None and unit.isClub():
            slotLabel = makeStaticSlotLabel(unitState, slotState, isPlayerCreator, vehCount, checkForVehicles, pInfo.isLegionary(), unit.isRated())
        else:
            isRequired = falloutBattleType == FALLOUT_BATTLE_TYPE.MULTITEAM
            slotLabel = makeSlotLabel(unitState, slotState, isPlayerCreator, vehCount, checkForVehicles, isRequired=isRequired)
        if unit.isSquad():
            playerStatus = getSquadPlayerStatus(slotState, player)
        else:
            playerStatus = getPlayerStatus(slotState, player)
        if unit is not None:
            restrictions = makeUnitRosterVO(unit, pInfo, index=index, isSortie=unit.isSortie(), levelsRange=levelsRange)['conditions']
        else:
            restrictions = []
        slot = {'rallyIdx': unitIdx,
         'isCommanderState': isPlayerCreator,
         'isCurrentUserInSlot': isPlayerInSlot,
         'playerStatus': playerStatus,
         'isClosed': slotState.isClosed,
         'isFreezed': unitState.isFreezed(),
         'slotLabel': slotLabel,
         'player': slotPlayerUI,
         'canBeTaken': canAssign and canTakeSlot,
         'compatibleVehiclesCount': vehCount,
         'selectedVehicle': vehicleVO,
         'selectedVehicleLevel': 1 if slotState.isClosed else slotLevel,
         'restrictions': restrictions,
         'isFallout': isFallout}
        if isFallout:
            vehiclesNotify = [None, None, None]
            selectedVehicles = [None, None, None]
            if player is not None:
                dbID = player.dbID
                isCurrentPlayer = player.isCurrentPlayer()
                if isCurrentPlayer:
                    falloutCtrl = getFalloutCtrl()
                    statusTemplate = None
                    if falloutBattleType == FALLOUT_BATTLE_TYPE.MULTITEAM:
                        if len(falloutCtrl.getSelectedVehicles()) < falloutCfg.minVehiclesPerPlayer:
                            statusTemplate = i18n.makeString(MESSENGER.DIALOGS_FALLOUTSQUADCHANNEL_VEHICLENOTIFYMULTITEAM)
                    elif falloutCtrl.mustSelectRequiredVehicle():
                        statusTemplate = i18n.makeString(MESSENGER.DIALOGS_FALLOUTSQUADCHANNEL_VEHICLENOTIFY, level=text_styles.main(int2roman(falloutCfg.vehicleLevelRequired)))
                    else:
                        statusTemplate = i18n.makeString(MESSENGER.DIALOGS_FALLOUTSQUADCHANNEL_VEHICLENOTIFYRANGE, level=text_styles.main(toRomanRangeString(list(falloutCfg.allowedLevels), 1)))
                    if statusTemplate is not None:
                        for slotIdx in range(falloutCfg.minVehiclesPerPlayer):
                            vehiclesNotify[slotIdx] = statusTemplate

                for idx, (vInvID, vehIntCD) in enumerate(unit.getExtra().accountVehicles.get(dbID, ())):
                    selectedVehicles[idx] = makeVehicleVO(vehicleGetter(vehIntCD), falloutCfg.allowedLevels, isCurrentPlayer=isCurrentPlayer)

            slot['vehiclesNotify'] = vehiclesNotify
            slot['selectedVehicle'] = selectedVehicles
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
        title = i18n.makeString(FORTIFICATIONS.SORTIE_LISTVIEW_ALERTTEXT_TITLE)
        body = i18n.makeString(FORTIFICATIONS.SORTIE_LISTVIEW_ALERTTEXT_BODY)
        alertView = {'icon': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON,
         'titleMsg': text_styles.alert(title),
         'bodyMsg': text_styles.main(body),
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
    week = text_styles.defRes(BigWorld.wg_getIntegralFormat(intWeekMining))
    allTime = text_styles.defRes(BigWorld.wg_getIntegralFormat(intTotalMining))
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


def makeStaticFormationUnitVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        isPlayerCreator = pInfo.isCreator()
        canDoAction, restriction = unitFunctional.validateLevels(stats=unitStats)
        sumLevelsStr = makeTotalLevelLabel(unitStats, restriction)
        return {'isCommander': isPlayerCreator,
         'statusLbl': makeStaticFormationStatusLbl(unitState),
         'statusValue': unitState.isOpened(),
         'sumLevelsInt': unitStats.curTotalLevel,
         'sumLevels': sumLevelsStr,
         'sumLevelsError': canDoAction,
         'slots': _getSlotsData(unitIdx, unit, unitState, pInfo, slotsIter, app, unitFunctional.getRosterSettings().getLevelsRange()),
         'description': unitFunctional.getCensoredComment(unitIdx=unitIdx)}


def makeStaticFormationStatusLbl(unitState):
    if unitState.isOpened():
        return CYBERSPORT.STATICFORMATION_UNITVIEW_OPENROOM_STATUS
    return CYBERSPORT.STATICFORMATION_UNITVIEW_CLOSEDROOM_STATUS


def makeSortieVO(unitFunctional, unitIdx = None, app = None):
    fullData = unitFunctional.getUnitFullData(unitIdx=unitIdx)
    if fullData is None:
        return {}
    else:
        unit, unitState, unitStats, pInfo, slotsIter = fullData
        division = getDivisionNameByType(unit.getRosterTypeID())
        divisionTypeStr = i18n.makeString(FORTIFICATIONS.sortie_division_name(division))
        divisionStr = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_DIVISION)
        divisionLbl = ''.join((text_styles.standard(divisionStr), text_styles.main(divisionTypeStr)))
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
        result = makeUnitRosterVO(unit, unitFunctional.getPlayerInfo(unitIdx=unitIdx), index=index, isSortie=unit.isSortie(), levelsRange=unitFunctional.getRosterSettings().getLevelsRange())
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
    defResCompensationValue = 0
    FORMAT_PATTERN = '###'
    if progress == FORT_ALIAS.STATE_FOUNDATION_DEF or progress == FORT_ALIAS.STATE_FOUNDATION:
        hpValueFormatter = text_styles.alert(FORMAT_PATTERN)
    else:
        hpValueFormatter = text_styles.defRes(FORMAT_PATTERN)
    hpTotalFormatted = str(BigWorld.wg_getIntegralFormat(hpTotalVal)) + ' '
    formattedHpTotal = ''.join((text_styles.standard(hpTotalFormatted), icons.nut()))
    defResValueFormatter = text_styles.alert(FORMAT_PATTERN) if defResVal > maxDefResVal else text_styles.defRes(FORMAT_PATTERN)
    maxDefDerFormatted = str(BigWorld.wg_getIntegralFormat(maxDefResVal)) + ' '
    formattedDefResTotal = ''.join((text_styles.standard(maxDefDerFormatted), icons.nut()))
    hpProgressLabels = {'currentValue': str(BigWorld.wg_getIntegralFormat(hpVal)),
     'currentValueFormatter': hpValueFormatter,
     'totalValue': formattedHpTotal,
     'separator': '/'}
    storeProgressLabels = {'currentValue': str(BigWorld.wg_getIntegralFormat(defResVal)),
     'currentValueFormatter': defResValueFormatter,
     'totalValue': formattedDefResTotal,
     'separator': '/'}
    result = {'hpLabel': i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_HPLBL),
     'defResLabel': i18n.makeString(FORTIFICATIONS.BUILDINGPOPOVER_INDICATORS_DEFRESLBL),
     'hpCurrentValue': hpVal,
     'hpTotalValue': hpTotalVal,
     'defResCurrentValue': defResVal,
     'defResCompensationValue': defResCompensationValue,
     'defResTotalValue': maxDefResVal,
     'hpProgressLabels': hpProgressLabels,
     'defResProgressLabels': storeProgressLabels}
    return result
