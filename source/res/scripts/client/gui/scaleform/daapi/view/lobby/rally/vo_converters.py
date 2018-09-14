# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/vo_converters.py
import BigWorld
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from constants import VEHICLE_CLASS_INDICES, VEHICLE_CLASSES, QUEUE_TYPE
from gui import makeHtmlString
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS, SLOT_LABEL
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES as FORT_ALIAS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control import settings
from gui.prb_control.items.sortie_items import getDivisionNameByType, getDivisionLevel
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED, Vehicle
from gui.shared.utils.functions import makeTooltip
from helpers import i18n, int2roman, dependency
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE, PROTO_TYPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from nations import INDICES as NATIONS_INDICES, NAMES as NATIONS_NAMES
from skeletons.gui.game_control import IFalloutController
from skeletons.gui.server_events import IEventsCache

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


def makeSlotLabel(unitFlags, slotState, isCreator=False, vehCount=0, checkForVehicles=True, isRequired=False):
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


def makeStaticSlotLabel(unitState, slotState, isCreator=False, vehCount=0, checkForVehicles=True, isLegionary=False, isRated=False):
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


def makeVehicleBasicVO(vehicle, levelsRange=None, vehicleTypes=None):
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
         'typeIndex': VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[vehicle.type],
         'smallIconPath': '../maps/icons/vehicle/small/{0}.png'.format(vehicle.name.replace(':', '-')),
         'isReadyToFight': True,
         'enabled': enabled,
         'tooltip': tooltip,
         'state': '',
         'isFalloutVehicle': vehicle.isFalloutSelected}


def makeVehicleVO(vehicle, levelsRange=None, vehicleTypes=None, isCurrentPlayer=True):
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


def makeIntroVehicleVO(vehicle, isReadyVehicle, warnTooltip, levelsRange=None, vehicleTypes=None, isCurrentPlayer=True):
    introVehicleVO = makeVehicleVO(vehicle)
    if introVehicleVO is None:
        return
    else:
        introVehicleVO['isReadyVehicle'] = isReadyVehicle
        introVehicleVO['warnTooltip'] = warnTooltip
        return introVehicleVO


def makeFiltersVO(nationIDRange, vTypeRange, vLevelRange):
    return {'nationIDRange': nationIDRange,
     'vTypeRange': vTypeRange,
     'vLevelRange': vLevelRange}


def makeUserVO(user, colorGetter, isPlayerSpeaking=False):
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


def makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking=False):
    if user is not None:
        colors = colorGetter(user.getGuiType())
        tags = list(user.getTags())
    else:
        colors = colorGetter(USER_GUI_TYPE.OTHER)
        tags = []
    return {'isInvite': pInfo.isInvite(),
     'dbID': pInfo.dbID,
     'accID': pInfo.accID,
     'isCommander': pInfo.isCommander(),
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


def makeSortiePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking=False):
    sortiePlayerVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    sortiePlayerVO['isLegionaries'] = pInfo.isLegionary()
    sortiePlayerVO['clanAbbrev'] = pInfo.clanAbbrev
    sortiePlayerVO['isRatingAvailable'] = pInfo.isLegionary()
    return sortiePlayerVO


def makeStaticFormationPlayerVO(pInfo, user, colorGetter, isPlayerSpeaking=False):
    staticFormationPlayerVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    staticFormationPlayerVO['isLegionaries'] = pInfo.isLegionary()
    staticFormationPlayerVO['isRatingAvailable'] = pInfo.isLegionary() and not pInfo.isInSlot
    return staticFormationPlayerVO


def makeClanBattlePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking=False):
    clanBattleVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    clanBattleVO['clanAbbrev'] = None
    clanBattleVO['isRatingAvailable'] = False
    return clanBattleVO


_UNIT_RESTRICTION_TO_LABEL = {UNIT_RESTRICTION.MAX_TOTAL_LEVEL: 'levelError',
 UNIT_RESTRICTION.MIN_TOTAL_LEVEL: 'levelError',
 UNIT_RESTRICTION.INVALID_TOTAL_LEVEL: 'levelWarning'}

def makeTotalLevelLabel(unitStats, restriction=''):
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


def _getSlotsData(unitIdx, fullData, app=None, levelsRange=None, checkForVehicles=True):
    pInfo = fullData.playerInfo
    isPlayerCreator = pInfo.isCommander()
    isPlayerInSlot = pInfo.isInSlot
    slots = []
    userGetter = storage_getter('users')().getUser
    colorGetter = g_settings.getColorScheme('rosters').getColors
    vehicleGetter = g_itemsCache.items.getItemByCD
    canTakeSlot = not pInfo.isLegionary()
    bwPlugin = proto_getter(PROTO_TYPE.BW_CHAT2)(None)
    isPlayerSpeaking = bwPlugin.voipController.isPlayerSpeaking
    falloutCtrl = dependency.instance(IFalloutController)
    isFallout = falloutCtrl.isEnabled()
    if isFallout:
        falloutBattleType = falloutCtrl.getBattleType()
        falloutCfg = falloutCtrl.getConfig()
    else:
        falloutBattleType = QUEUE_TYPE.UNKNOWN
        falloutCfg = None
    unit = fullData.unit
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
    rosterSlots = {}
    isDefaultSlot = False
    if unit is not None:
        roster = unit.getRoster()
        rosterSlots = roster.slots
        isDefaultSlot = roster.isDefaultSlot
    unitState = fullData.flags
    for slotInfo in fullData.slotsIterator:
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
                slotLevel = vehicle.vehLevel
                if vehicle.vehTypeCompDescr:
                    vehicleVO = makeVehicleVO(vehicleGetter(vehicle.vehTypeCompDescr), levelsRange, isCurrentPlayer=isCurrentPlayer)
        if unit is not None and unit.isClub():
            slotLabel = makeStaticSlotLabel(unitState, slotState, isPlayerCreator, vehCount, checkForVehicles, pInfo.isLegionary(), unit.isRated())
        else:
            isRequired = falloutBattleType == QUEUE_TYPE.FALLOUT_MULTITEAM
            slotLabel = makeSlotLabel(unitState, slotState, isPlayerCreator, vehCount, checkForVehicles, isRequired=isRequired)
        if unit.isPrebattlesSquad():
            playerStatus = getSquadPlayerStatus(slotState, player)
        else:
            playerStatus = getPlayerStatus(slotState, player)
        if unit is not None:
            restrictions = makeUnitRosterConditions(rosterSlots, isDefaultSlot, index=index, isSortie=unit.isSortie(), levelsRange=levelsRange)
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
        if unit.isSquad():
            eventsCache = dependency.instance(IEventsCache)
            if eventsCache.isBalancedSquadEnabled():
                isVisibleAdtMsg = player and player.isCurrentPlayer() and not isPlayerCreator and not vehicle and unit and bool(unit.getVehicles())
                if isVisibleAdtMsg:
                    rangeString = toRomanRangeString(levelsRange, 1)
                    additionMsg = text_styles.main(i18n.makeString(MESSENGER.DIALOGS_SIMPLESQUAD_VEHICLELEVEL, level=rangeString))
                else:
                    additionMsg = ''
                slot.update({'isVisibleAdtMsg': isVisibleAdtMsg,
                 'additionalMsg': additionMsg})
            elif eventsCache.isSquadXpFactorsEnabled():
                vehicles = unit.getVehicles()
                levels = unit.getSelectedVehicleLevels()
                isVisibleAdtMsg = False
                additionalMsg = ''
                unitHasXpBonus = True
                unitHasXpPenalty = False
                if vehicles:
                    distance = levels[-1] - levels[0]
                    unitHasXpBonus = distance in eventsCache.getSquadBonusLevelDistance()
                    unitHasXpPenalty = distance in eventsCache.getSquadPenaltyLevelDistance()
                    isVisibleAdtMsg = unitHasXpBonus and player and player.isCurrentPlayer() and not vehicle
                    if isVisibleAdtMsg:
                        maxDistance = max(eventsCache.getSquadBonusLevelDistance())
                        minLevel = max(MIN_VEHICLE_LEVEL, levels[0] - maxDistance)
                        maxLevel = min(MAX_VEHICLE_LEVEL, levels[0] + maxDistance)
                        rangeString = toRomanRangeString(range(minLevel, maxLevel + 1), 1)
                        additionalMsg = text_styles.main(i18n.makeString(MESSENGER.DIALOGS_SIMPLESQUAD_VEHICLELEVEL, level=rangeString))
                slotNotificationIcon = ''
                slotNotificationIconTooltip = ''
                if vehicle:
                    if unitHasXpPenalty:
                        slotNotificationIcon = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_ALERTICON
                        slotNotificationIconTooltip = makeTooltip(TOOLTIPS.SQUADWINDOW_SIMPLESLOTNOTIFICATION_ALERT_HEADER, TOOLTIPS.SQUADWINDOW_SIMPLESLOTNOTIFICATION_ALERT_BODY, None, TOOLTIPS.SQUADWINDOW_SIMPLESLOTNOTIFICATION_ALERT_ALERT)
                    elif not unitHasXpBonus:
                        slotNotificationIcon = RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON
                        slotNotificationIconTooltip = makeTooltip(TOOLTIPS.SQUADWINDOW_SIMPLESLOTNOTIFICATION_INFO_HEADER, TOOLTIPS.SQUADWINDOW_SIMPLESLOTNOTIFICATION_INFO_BODY)
                slot.update({'isVisibleAdtMsg': isVisibleAdtMsg,
                 'additionalMsg': additionalMsg,
                 'slotNotificationIconTooltip': slotNotificationIconTooltip,
                 'slotNotificationIcon': slotNotificationIcon})
        if unit.isEvent():
            isVisibleAdtMsg = player and player.isCurrentPlayer() and not vehicle
            additionMsg = ''
            if isVisibleAdtMsg:
                eventsCache = dependency.instance(IEventsCache)
                vehiclesNames = [ veh.userName for veh in eventsCache.getEventVehicles() ]
                additionMsg = text_styles.main(i18n.makeString(MESSENGER.DIALOGS_EVENTSQUAD_VEHICLE, vehName=', '.join(vehiclesNames)))
            slot.update({'isVisibleAdtMsg': isVisibleAdtMsg,
             'additionalMsg': additionMsg})
        if isFallout:
            vehiclesNotify = [None, None, None]
            selectedVehicles = [None, None, None]
            if player is not None:
                dbID = player.dbID
                isCurrentPlayer = player.isCurrentPlayer()
                if isCurrentPlayer:
                    statusTemplate = None
                    if falloutBattleType == QUEUE_TYPE.FALLOUT_MULTITEAM:
                        minVehiclesPerPlayer = falloutCfg.minVehiclesPerPlayer
                        if len(falloutCtrl.getSelectedVehicles()) < minVehiclesPerPlayer:
                            statusTemplate = i18n.makeString(MESSENGER.DIALOGS_FALLOUTSQUADCHANNEL_VEHICLENOTIFYMULTITEAM)
                    elif falloutCtrl.mustSelectRequiredVehicle():
                        statusTemplate = i18n.makeString(MESSENGER.DIALOGS_FALLOUTSQUADCHANNEL_VEHICLENOTIFY, level=text_styles.main(int2roman(falloutCfg.vehicleLevelRequired)))
                    else:
                        statusTemplate = i18n.makeString(MESSENGER.DIALOGS_FALLOUTSQUADCHANNEL_VEHICLENOTIFYRANGE, level=text_styles.main(toRomanRangeString(list(falloutCfg.allowedLevels), 1)))
                    if statusTemplate is not None:
                        for slotIdx in range(falloutCfg.minVehiclesPerPlayer):
                            vehiclesNotify[slotIdx] = statusTemplate

                for idx, vehicle in enumerate(unit.getVehicles().get(dbID, ())):
                    selectedVehicles[idx] = makeVehicleVO(vehicleGetter(vehicle.vehTypeCompDescr), falloutCfg.allowedLevels, isCurrentPlayer=isCurrentPlayer)

            slot['vehiclesNotify'] = vehiclesNotify
            slot['selectedVehicle'] = selectedVehicles
        slots.append(slot)

    return slots


def makeSlotsVOs(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    slots = _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange())
    isRosterSet = fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES)
    return (isRosterSet, slots)


def getUnitMaxLevel(unitEntity, unitIdx=None, app=None):
    _, unit = unitEntity.getUnit(unitIdx=unitIdx)
    division = getDivisionNameByType(unit.getRosterTypeID())
    return getDivisionLevel(division)


def makeUnitShortVO(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    return {'isFreezed': fullData.flags.isLocked(),
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'slots': _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange()),
     'description': unitEntity.getCensoredComment(unitIdx=unitIdx)}


def makeSortieShortVO(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    division = getDivisionNameByType(fullData.unit.getRosterTypeID())
    divisionTypeStr = i18n.makeString(FORTIFICATIONS.sortie_division_name(division))
    if divisionTypeStr:
        description = divisionTypeStr
    else:
        description = unitEntity.getCensoredComment(unitIdx=unitIdx)
    return {'isFreezed': fullData.flags.isLocked(),
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'slots': _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange()),
     'description': description}


def makeMsg(value):
    return i18n.makeString(value)


def makeFortBattleShortVO(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    return {'isFreezed': fullData.flags.isLocked(),
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'slots': _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange()),
     'description': unitEntity.getCensoredComment(unitIdx=unitIdx)}


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


def makeUnitVO(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    isPlayerCreator = fullData.playerInfo.isCommander()
    levelsValidation = unitEntity.validateLevels()
    canDoAction, restriction = levelsValidation.isValid, levelsValidation.restriction
    sumLevelsStr = makeTotalLevelLabel(fullData.stats, restriction)
    return {'isCommander': isPlayerCreator,
     'isFreezed': fullData.flags.isLocked(),
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'statusLbl': makeUnitStateLabel(fullData.flags),
     'statusValue': fullData.flags.isOpened(),
     'sumLevelsInt': fullData.stats.curTotalLevel,
     'sumLevels': sumLevelsStr,
     'sumLevelsError': canDoAction,
     'slots': _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange()),
     'description': unitEntity.getCensoredComment(unitIdx=unitIdx)}


def makeStaticFormationUnitVO(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    isPlayerCreator = fullData.playerInfo.isCommander()
    levelsValidation = unitEntity.validateLevels()
    canDoAction, restriction = levelsValidation.isValid, levelsValidation.restriction
    sumLevelsStr = makeTotalLevelLabel(fullData.stats, restriction)
    return {'isCommander': isPlayerCreator,
     'statusLbl': makeStaticFormationStatusLbl(fullData.flags),
     'statusValue': fullData.flags.isOpened(),
     'sumLevelsInt': fullData.stats.curTotalLevel,
     'sumLevels': sumLevelsStr,
     'sumLevelsError': canDoAction,
     'slots': _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange()),
     'description': unitEntity.getCensoredComment(unitIdx=unitIdx)}


def makeStaticFormationStatusLbl(unitState):
    return CYBERSPORT.STATICFORMATION_UNITVIEW_OPENROOM_STATUS if unitState.isOpened() else CYBERSPORT.STATICFORMATION_UNITVIEW_CLOSEDROOM_STATUS


def makeSortieVO(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    division = getDivisionNameByType(fullData.unit.getRosterTypeID())
    divisionTypeStr = i18n.makeString(FORTIFICATIONS.sortie_division_name(division))
    divisionStr = i18n.makeString(FORTIFICATIONS.SORTIE_ROOM_DIVISION)
    divisionLbl = ''.join((text_styles.standard(divisionStr), text_styles.main(divisionTypeStr)))
    isPlayerCreator = fullData.playerInfo.isCommander()
    levelsValidation = unitEntity.validateLevels()
    canDoAction, restriction = levelsValidation.isValid, levelsValidation.restriction
    sumLevelsStr = makeTotalLevelLabel(fullData.stats, restriction)
    return {'isCommander': isPlayerCreator,
     'isFreezed': fullData.flags.isLocked(),
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'statusLbl': makeUnitStateLabel(fullData.flags),
     'statusValue': fullData.flags.isOpened(),
     'sumLevelsInt': fullData.stats.curTotalLevel,
     'sumLevels': sumLevelsStr,
     'sumLevelsError': canDoAction,
     'slots': _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange()),
     'description': unitEntity.getCensoredComment(unitIdx=unitIdx),
     'divisionLbl': divisionLbl}


def makeFortBattleVO(unitEntity, unitIdx=None, app=None):
    fullData = unitEntity.getUnitFullData(unitIdx=unitIdx)
    isPlayerCreator = fullData.playerInfo.isCommander()
    levelsValidation = unitEntity.validateLevels()
    canDoAction, restriction = levelsValidation.isValid, levelsValidation.restriction
    sumLevelsStr = makeTotalLevelLabel(fullData.stats, restriction)
    return {'isCommander': isPlayerCreator,
     'isFreezed': fullData.flags.isLocked(),
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'statusLbl': makeUnitStateLabel(fullData.flags),
     'statusValue': fullData.flags.isOpened(),
     'sumLevelsInt': fullData.stats.curTotalLevel,
     'sumLevels': sumLevelsStr,
     'sumLevelsError': canDoAction,
     'slots': _getSlotsData(unitIdx, fullData, app, unitEntity.getRosterSettings().getLevelsRange()),
     'description': unitEntity.getCensoredComment(unitIdx=unitIdx)}


def makeUnitRosterVO(unit, pInfo, index=None, isSortie=False, levelsRange=None):
    vehicleGetter = g_itemsCache.items.getItemByCD
    if index is None:
        vehiclesData = pInfo.getVehiclesToSlots().keys()
    else:
        vehiclesData = pInfo.getVehiclesToSlot(index)
    vehicleVOs = map(lambda vehTypeCD: makeVehicleVO(vehicleGetter(vehTypeCD)), vehiclesData)
    roster = unit.getRoster()
    rosterSlots = roster.slots
    isDefaultSlot = roster.isDefaultSlot
    return getUnitRosterModel(vehicleVOs, makeUnitRosterConditions(rosterSlots, isDefaultSlot, index, isSortie, levelsRange), pInfo.isCommander())


def makeUnitRosterConditions(slots, isDefaultSlot, index=None, isSortie=False, levelsRange=None):
    if index is None:
        return [None, None]
    else:
        vehicleGetter = g_itemsCache.items.getItemByCD
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
            params = {'nationIDRange': tuple(),
             'vTypeRange': tuple(),
             'vLevelRange': tuple()}
            isDefault = not isSortie and isDefaultSlot(rosterSlot)
            if not isDefault:
                if not rosterSlot.isNationMaskFull():
                    nationMask = rosterSlot.nationMask
                    params['nationIDRange'] = filter(lambda k: 1 << NATIONS_INDICES[k] & nationMask, NATIONS_NAMES)
                if not rosterSlot.isVehClassMaskFull():
                    vehClassMask = rosterSlot.vehClassMask
                    params['vTypeRange'] = filter(lambda k: 1 << VEHICLE_CLASS_INDICES[k] & vehClassMask, VEHICLE_CLASSES)
                levels = rosterSlot.levels
                if levels != rosterSlot.DEFAULT_LEVELS or isSortie:
                    params['vLevelRange'] = levels
                conditions.append(params)
            conditions.append(None)

        return conditions


def getUnitRosterModel(vehiclesData, conditions, isCreator):
    return {'vehicles': vehiclesData,
     'conditions': conditions,
     'isCreator': isCreator}


def getUnitRosterData(unitEntity, unitIdx=None, index=None):
    _, unit = unitEntity.getUnit(unitIdx)
    if unit is None:
        result = {}
    else:
        result = makeUnitRosterVO(unit, unitEntity.getPlayerInfo(unitIdx=unitIdx), index=index, isSortie=unit.isSortie(), levelsRange=unitEntity.getRosterSettings().getLevelsRange())
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
     'defResCompensationValue': max(0, defResVal - maxDefResVal),
     'defResTotalValue': maxDefResVal,
     'hpProgressLabels': hpProgressLabels,
     'defResProgressLabels': storeProgressLabels}
    return result
