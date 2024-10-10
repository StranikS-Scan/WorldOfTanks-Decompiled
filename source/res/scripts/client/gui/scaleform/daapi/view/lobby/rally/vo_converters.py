# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/vo_converters.py
import BigWorld
from UnitBase import UNIT_ROLE
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL, PREBATTLE_TYPE
from constants import VEHICLE_CLASS_INDICES, VEHICLE_CLASSES
from gui import makeHtmlString
from gui.Scaleform.settings import ICONS_SIZES
from helpers import dependency
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.shared.utils.functions import getArenaShortName
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS, SLOT_LABEL
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES as FORT_ALIAS
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.PLATOON import PLATOON
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.prb_control import settings
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.formatters import icons, text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED, Vehicle, getIconResourceName
from gui.shared.utils.functions import makeTooltip
from gui.prb_control.items.stronghold_items import SUPPORT_TYPE, REQUISITION_TYPE, HEAVYTRUCKS_TYPE, BOOST_TYPE, ARTILLERY_STRIKE, REQUISITION, HIGH_CAPACITY_TRANSPORT, INSPIRATION
from helpers import i18n
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE, PROTO_TYPE, USER_TAG
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from nations import INDICES as NATIONS_INDICES, NAMES as NATIONS_NAMES
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEpicBattleMetaGameController
MAX_PLAYER_COUNT_ALL = 0

def getPlayerStatus(slotState, pInfo):
    if slotState.isClosed:
        return PLAYER_GUI_STATUS.LOCKED
    else:
        if pInfo is not None:
            if pInfo.isInArena() or pInfo.isInSearch() or pInfo.isInQueue():
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


def makeSlotLabel(unitFlags, slotState, isCreator=False, vehCount=0, checkForVehicles=True, isRequired=False, ignoreIfEmpty=False):
    slotLabel = SLOT_LABEL.DEFAULT
    if slotState.isFree:
        if unitFlags.isLocked():
            template = SLOT_LABEL.LOCKED
        elif not isCreator and checkForVehicles and vehCount == 0:
            template = SLOT_LABEL.NOT_AVAILABLE
        elif isCreator and isRequired:
            template = SLOT_LABEL.REQUIRED
        else:
            if ignoreIfEmpty:
                return ''
            template = SLOT_LABEL.EMPTY
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', template)
    elif slotState.isClosed:
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', SLOT_LABEL.CLOSED)
    return slotLabel


def makeBattleRoyaleSlotLabel(slotState):
    slotLabel = SLOT_LABEL.DEFAULT
    if slotState.isFree:
        slotLabel = makeHtmlString('html_templates:lobby/cyberSport/unit', SLOT_LABEL.BATTLE_ROYALE)
    return slotLabel


def makeVehicleBasicVO(vehicle, levelsRange=None, vehicleTypes=None):
    if vehicle is None:
        return
    else:
        isBattleRoyaleVehicle = vehicle.isOnlyForBattleRoyaleBattles
        enabled, tooltip = True, None
        if levelsRange is not None and vehicle.level not in levelsRange:
            enabled, tooltip = False, TOOLTIPS.VEHICLESELECTOR_OVERFLOWLEVEL
        elif vehicleTypes is not None and vehicle.type not in vehicleTypes:
            enabled, tooltip = False, TOOLTIPS.VEHICLESELECTOR_INCOMPATIBLETYPE
        elif isBattleRoyaleVehicle:
            enabled, tooltip = True, TOOLTIPS_CONSTANTS.BATTLE_ROYALE_VEHICLE
        iconPath = backport.image(R.images.gui.maps.icons.vehicle.small.dyn(getIconResourceName(vehicle.name))())
        return {'intCD': vehicle.intCD,
         'nationID': vehicle.nationID,
         'name': vehicle.name,
         'userName': vehicle.userName,
         'shortUserName': vehicle.shortUserName,
         'level': vehicle.level if not vehicle.isOnlyForBattleRoyaleBattles else 0,
         'type': vehicle.type if not vehicle.isOnlyForBattleRoyaleBattles else '',
         'typeIndex': VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[vehicle.type],
         'smallIconPath': iconPath,
         'isReadyToFight': True,
         'enabled': enabled,
         'tooltip': tooltip,
         'state': '',
         'isEventVehicle': isBattleRoyaleVehicle}


def makeVehicleVO(vehicle, levelsRange=None, vehicleTypes=None, isCurrentPlayer=True):
    vehicleVO = makeVehicleBasicVO(vehicle, levelsRange, vehicleTypes)
    if vehicleVO is None:
        return
    else:
        vState, _ = vehicle.getState(isCurrentPlayer)
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


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def makeUserVO(user, colorGetter, isPlayerSpeaking=False, lobbyContext=None):
    if user is not None:
        colors = colorGetter(user.getGuiType())
        tags = list(user.getTags())
    else:
        colors = colorGetter(USER_GUI_TYPE.OTHER)
        tags = []
    if lobbyContext is not None:
        regionCode = lobbyContext.getRegionCode(user.getID())
    else:
        regionCode = None
    return {'isInvite': False,
     'dbID': user.getID(),
     'accID': -1,
     'isCommander': True,
     'userName': user.getName(),
     'fullName': user.getFullName(),
     'clanAbbrev': user.getClanAbbrev(),
     'region': regionCode,
     'colors': colors,
     'rating': None,
     'readyState': False,
     'tags': tags,
     'isPlayerSpeaking': isPlayerSpeaking,
     'isOffline': not user.isOnline(),
     'igrType': 0,
     'isRatingAvailable': True}


def makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking=False, isIncludeAccountWTR=False):
    if user is not None:
        colors = colorGetter(user.getGuiType())
        tags = list(user.getTags())
    else:
        colors = colorGetter(USER_GUI_TYPE.OTHER)
        tags = []
    rating = backport.getIntegralFormat(pInfo.rating)
    badge = pInfo.getBadge()
    badgeVO = badge.getBadgeVO(ICONS_SIZES.X24, {'isAtlasSource': False}) if badge else {}
    playerVO = {'isInvite': pInfo.isInvite(),
     'dbID': pInfo.dbID,
     'accID': pInfo.accID,
     'isCommander': pInfo.isCommander(),
     'userName': pInfo.name,
     'fullName': pInfo.getFullName(),
     'clanAbbrev': pInfo.clanAbbrev,
     'region': pInfo.getRegion(),
     'colors': colors,
     'rating': rating,
     'readyState': pInfo.isReady,
     'tags': tags,
     'isPlayerSpeaking': isPlayerSpeaking,
     'isOffline': pInfo.isOffline(),
     'igrType': pInfo.igrType,
     'isRatingAvailable': True,
     'badgeVisualVO': badgeVO,
     'timeJoin': pInfo.getTimeJoin(),
     'extraData': pInfo.getExtraData()}
    if isIncludeAccountWTR:
        playerVO['accountWTR'] = backport.getIntegralFormat(pInfo.accountWTR) if pInfo.accountWTR else '-'
    return playerVO


def makeSortiePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking=False):
    sortiePlayerVO = makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)
    sortiePlayerVO['isLegionaries'] = True
    sortiePlayerVO['clanAbbrev'] = pInfo.clanAbbrev
    sortiePlayerVO['isRatingAvailable'] = True
    sortiePlayerVO['statusIcon'] = makeCandidateIconPath(pInfo, user)
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


def makeCandidateIconPath(pInfo, user):
    tags = user.getTags() if user else {}
    if USER_TAG.PRESENCE_DND in tags:
        return RES_ICONS.MAPS_ICONS_LIBRARY_USERSTATUS_SMALL_BUSY
    return RES_ICONS.MAPS_ICONS_LIBRARY_USERSTATUS_SMALL_ONLINE if USER_TAG.FRIEND in tags and USER_TAG.SUB_PENDING_OUT not in tags and USER_TAG.SUB_NONE not in tags or USER_TAG.CLAN_MEMBER in tags else RES_ICONS.MAPS_ICONS_LIBRARY_USERSTATUS_SMALL_OFFLINE


_UNIT_RESTRICTION_TO_LABEL = {UNIT_RESTRICTION.MAX_TOTAL_LEVEL: 'levelError',
 UNIT_RESTRICTION.MIN_TOTAL_LEVEL: 'levelError',
 UNIT_RESTRICTION.INVALID_TOTAL_LEVEL: 'levelWarning'}
_ROLE_ICONS = {UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS: 'gunner',
 UNIT_ROLE.CAN_USE_BOOST_EQUIPMENTS: 'inspire',
 UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS | UNIT_ROLE.CAN_USE_BOOST_EQUIPMENTS: 'gunnerAndInspire'}

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


def _getSlotsData(unitMgrID, fullData, levelsRange=None, checkForVehicles=True, maxPlayerCount=MAX_PLAYER_COUNT_ALL, withPrem=False):
    pInfo = fullData.playerInfo
    isPlayerCreator = pInfo.isCommander()
    isPlayerInSlot = pInfo.isInSlot
    slots = []
    userGetter = storage_getter('users')().getUser
    colorGetter = g_settings.getColorScheme('rosters').getColors
    itemsCache = dependency.instance(IItemsCache)
    vehicleGetter = itemsCache.items.getItemByCD
    lobbyContext = dependency.instance(ILobbyContext)
    squadPremBonusEnabled = lobbyContext.getServerSettings().squadPremiumBonus.isEnabled
    canTakeSlot = not pInfo.isLegionary()
    bwPlugin = proto_getter(PROTO_TYPE.BW_CHAT2)(None)
    isPlayerSpeaking = bwPlugin.voipController.isPlayerSpeaking
    unit = fullData.unit
    rosterSlots = {}
    isDefaultSlot = False
    isIncludeAccountWTR = False
    if unit is not None:
        roster = unit.getRoster()
        rosterSlots = roster.slots
        isDefaultSlot = roster.isDefaultSlot
        if unit.getPrebattleType() in PREBATTLE_TYPE.EXTERNAL_PREBATTLES:
            canTakeSlot = canTakeSlot and not isPlayerInSlot
        if unit.getPrebattleType() in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            isIncludeAccountWTR = True
    unitState = fullData.flags
    playerCount = 0
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
            slotPlayerUI = makePlayerVO(player, userGetter(dbID), colorGetter, isPlayerSpeaking(dbID), isIncludeAccountWTR=isIncludeAccountWTR)
            isCurrentPlayer = player.isCurrentPlayer()
            if vehicle:
                slotLevel = vehicle.vehLevel
                if vehicle.vehTypeCompDescr:
                    vehicleVO = makeVehicleVO(vehicleGetter(vehicle.vehTypeCompDescr), levelsRange, isCurrentPlayer=isCurrentPlayer)
        isRequired = False
        if unit is not None and unit.getPrebattleType() == PREBATTLE_TYPE.BATTLE_ROYALE:
            slotLabel = makeBattleRoyaleSlotLabel(slotState)
        else:
            ignoreEmptySlot = unit is not None and unit.getPrebattleType() in PREBATTLE_TYPE.SQUAD_PREBATTLES
            slotLabel = makeSlotLabel(unitState, slotState, isPlayerCreator, vehCount, checkForVehicles, isRequired=isRequired, ignoreIfEmpty=ignoreEmptySlot)
        if unit.isPrebattlesSquad():
            playerStatus = getSquadPlayerStatus(slotState, player)
        else:
            playerStatus = getPlayerStatus(slotState, player)
        if unit is not None:
            restrictions = makeUnitRosterConditions(rosterSlots, isDefaultSlot, index=index, levelsRange=levelsRange)
        else:
            restrictions = []
        rating = ''
        isLegionaries = False
        role = 0
        if player is not None:
            isLegionaries = player.isLegionary()
            rating = backport.getIntegralFormat(player.rating)
            role = player.role
        if maxPlayerCount == MAX_PLAYER_COUNT_ALL or playerCount < maxPlayerCount:
            isLocked = False
        else:
            isLocked = True
        equipmentCommanderRoles = UNIT_ROLE.CAN_USE_BOOST_EQUIPMENTS | UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS
        slot = {'rallyIdx': unitMgrID,
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
         'isEvent': False,
         'rating': rating,
         'isLegionaries': isLegionaries,
         'isLocked': isLocked,
         'role': role,
         'roleIcon': _ROLE_ICONS.get(role & equipmentCommanderRoles, '')}
        if withPrem:
            slot['hasPremiumAccount'] = player and player.hasPremium
        if unit.isSquad() or unit.getPrebattleType() == PREBATTLE_TYPE.FUN_RANDOM:
            eventsCache = dependency.instance(IEventsCache)
            if eventsCache.isBalancedSquadEnabled():
                slot.update(_getBalancedSquadInfo(isPlayerCreator, levelsRange, player, unit, vehicle))
            elif eventsCache.isSquadXpFactorsEnabled():
                slot.update(_getXPFactorSlotInfo(unit, eventsCache, slotInfo))
        if unit.isEvent():
            isVisibleAdtMsg = player and player.isCurrentPlayer() and vehicle is not None
            additionMsg = ''
            if isVisibleAdtMsg:
                additionMsg = backport.text(R.strings.event.simpleSquad.selectRestriction())
            slot.update({'isVisibleAdtMsg': isVisibleAdtMsg,
             'additionalMsg': additionMsg})
        elif unit.getPrebattleType() == PREBATTLE_TYPE.EPIC and squadPremBonusEnabled:
            slot.update(_updateEpicBattleSlotInfo(player, vehicle))
        slots.append(slot)
        playerCount += 1

    return slots


def _getBalancedSquadInfo(isPlayerCreator, levelsRange, player, unit, vehicle):
    isVisibleAdtMsg = player and player.isCurrentPlayer() and not isPlayerCreator and not vehicle and unit and bool(unit.getVehicles())
    if isVisibleAdtMsg:
        rangeString = toRomanRangeString(levelsRange, 1)
        additionMsg = i18n.makeString(PLATOON.MEMBERS_CARD_SELECTVEHICLE, level=rangeString)
    else:
        additionMsg = ''
    return {'isVisibleAdtMsg': isVisibleAdtMsg,
     'additionalMsg': additionMsg}


@dependency.replace_none_kwargs(epicMetaGameController=IEpicBattleMetaGameController)
def _updateEpicBattleSlotInfo(player, vehicle, epicMetaGameController=None):
    return _updateSpecialBattleSlotInfo(player, vehicle, backport.text(R.strings.messenger.dialogs.simpleSquad.epicBattle.VehicleRestriction(), level=epicMetaGameController.getSuitableForQueueVehicleLevelStr()))


def _updateSpecialBattleSlotInfo(player, vehicle, message):
    result = {}
    if vehicle is None:
        isVisibleAdtMsg = player and player.isCurrentPlayer()
        additionalMsg = message
        result = {'isVisibleAdtMsg': isVisibleAdtMsg,
         'additionalMsg': additionalMsg}
    return result


def _getXPFactorSlotInfo(unit, eventsCache, slotInfo):
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
        isVisibleAdtMsg = unitHasXpBonus and slotInfo.player and slotInfo.player.isCurrentPlayer() and not slotInfo.vehicle
        if isVisibleAdtMsg:
            maxDistance = max(eventsCache.getSquadBonusLevelDistance())
            minLevel = max(MIN_VEHICLE_LEVEL, levels[0] - maxDistance)
            maxLevel = min(MAX_VEHICLE_LEVEL, levels[0] + maxDistance)
            rangeString = toRomanRangeString(range(minLevel, maxLevel + 1), 1)
            additionalMsg = i18n.makeString(PLATOON.MEMBERS_CARD_SELECTVEHICLE, level=rangeString)
    slotNotificationIcon = ''
    if slotInfo.vehicle:
        if unitHasXpPenalty:
            slotNotificationIcon = RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_ALERTICON
        elif not unitHasXpBonus:
            slotNotificationIcon = RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON
    return {'isVisibleAdtMsg': isVisibleAdtMsg,
     'additionalMsg': additionalMsg,
     'slotNotificationIcon': slotNotificationIcon}


def makeSlotsVOs(unitEntity, unitMgrID=None, maxPlayerCount=MAX_PLAYER_COUNT_ALL, withPrem=False):
    fullData = unitEntity.getUnitFullData(unitMgrID=unitMgrID)
    if fullData is None or fullData.unit is None:
        return (False, {})
    else:
        slots = _getSlotsData(unitMgrID, fullData, unitEntity.getRosterSettings().getLevelsRange(), maxPlayerCount=maxPlayerCount, withPrem=withPrem)
        isRosterSet = fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES)
        return (isRosterSet, slots)


def makeUnitShortVO(unitEntity, unitMgrID=None, maxPlayerCount=MAX_PLAYER_COUNT_ALL):
    fullData = unitEntity.getUnitFullData(unitMgrID=unitMgrID)
    return {'isFreezed': fullData.flags.isLocked(),
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'slots': _getSlotsData(unitMgrID, fullData, unitEntity.getRosterSettings().getLevelsRange(), maxPlayerCount=maxPlayerCount),
     'description': unitEntity.getCensoredComment(unitMgrID=unitMgrID)}


def makeMsg(value):
    return i18n.makeString(value)


def makeSimpleClanListRenderVO(member, intTotalMining, intWeekMining, role, roleID):
    week = text_styles.defRes(backport.getIntegralFormat(intWeekMining))
    allTime = text_styles.defRes(backport.getIntegralFormat(intTotalMining))
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


def makeUnitVO(unitEntity, unitMgrID=None, maxPlayerCount=MAX_PLAYER_COUNT_ALL, withPrem=False):
    fullData = unitEntity.getUnitFullData(unitMgrID=unitMgrID)
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
     'slots': _getSlotsData(unitMgrID, fullData, unitEntity.getRosterSettings().getLevelsRange(), maxPlayerCount=maxPlayerCount, withPrem=withPrem),
     'description': unitEntity.getCensoredComment(unitMgrID=unitMgrID)}


def makeUnitRosterVO(unit, pInfo, index=None, levelsRange=None):
    itemsCache = dependency.instance(IItemsCache)
    vehicleGetter = itemsCache.items.getItemByCD
    if index is None:
        vehiclesData = pInfo.getVehiclesToSlots().keys()
    else:
        vehiclesData = pInfo.getVehiclesToSlot(index)
    vehicleVOs = [ makeVehicleVO(vehicleGetter(vehTypeCD)) for vehTypeCD in vehiclesData ]
    roster = unit.getRoster()
    rosterSlots = roster.slots
    isDefaultSlot = roster.isDefaultSlot
    return getUnitRosterModel(vehicleVOs, makeUnitRosterConditions(rosterSlots, isDefaultSlot, index, levelsRange), pInfo.isCommander())


def makeUnitRosterConditions(slots, isDefaultSlot, index=None, levelsRange=None):
    if index is None:
        return [None, None]
    else:
        itemsCache = dependency.instance(IItemsCache)
        vehicleGetter = itemsCache.items.getItemByCD
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
            isDefault = isDefaultSlot(rosterSlot)
            if not isDefault:
                if not rosterSlot.isNationMaskFull():
                    nationMask = rosterSlot.nationMask
                    params['nationIDRange'] = filter(lambda k, mask=nationMask: 1 << NATIONS_INDICES[k] & mask, NATIONS_NAMES)
                if not rosterSlot.isVehClassMaskFull():
                    vehClassMask = rosterSlot.vehClassMask
                    params['vTypeRange'] = filter(lambda k, mask=vehClassMask: 1 << VEHICLE_CLASS_INDICES[k] & mask, VEHICLE_CLASSES)
                levels = rosterSlot.levels
                if levels != rosterSlot.DEFAULT_LEVELS:
                    params['vLevelRange'] = levels
                conditions.append(params)
            conditions.append(None)

        return conditions


def getUnitRosterModel(vehiclesData, conditions, isCreator):
    return {'vehicles': vehiclesData,
     'conditions': conditions,
     'isCreator': isCreator}


def getUnitRosterData(unitEntity, unitMgrID=None, index=None):
    _, unit = unitEntity.getUnit(unitMgrID)
    if unit is None:
        result = {}
    else:
        result = makeUnitRosterVO(unit, unitEntity.getPlayerInfo(unitMgrID=unitMgrID), index=index, levelsRange=unitEntity.getRosterSettings().getLevelsRange())
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
    hpTotalFormatted = str(backport.getIntegralFormat(hpTotalVal)) + ' '
    formattedHpTotal = ''.join((text_styles.standard(hpTotalFormatted), icons.nut()))
    defResValueFormatter = text_styles.alert(FORMAT_PATTERN) if defResVal > maxDefResVal else text_styles.defRes(FORMAT_PATTERN)
    maxDefDerFormatted = str(backport.getIntegralFormat(maxDefResVal)) + ' '
    formattedDefResTotal = ''.join((text_styles.standard(maxDefDerFormatted), icons.nut()))
    hpProgressLabels = {'currentValue': str(backport.getIntegralFormat(hpVal)),
     'currentValueFormatter': hpValueFormatter,
     'totalValue': formattedHpTotal,
     'separator': '/'}
    storeProgressLabels = {'currentValue': str(backport.getIntegralFormat(defResVal)),
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


__emptyTypeMap = {SUPPORT_TYPE: 'fireSupportPlus',
 BOOST_TYPE: 'inspirePlus',
 REQUISITION_TYPE: 'requisitionPlus',
 HEAVYTRUCKS_TYPE: 'heavyTrucksPlus'}

def makeReserveSlotVO(reserveType, groupType, reserveId, level, slotIndex, tooltip, tooltipType):
    if reserveType is None:
        slotType = __emptyTypeMap[groupType]
    else:
        slotType = getReserveNameVO(reserveType)
    return {'slotType': slotType,
     'level': level,
     'slotIndex': slotIndex,
     'id': reserveId,
     'tooltipType': tooltipType,
     'tooltip': tooltip}


__locTypeMap = {SUPPORT_TYPE: FORTIFICATIONS.STRONGHOLDRESERVE_SUPPORT,
 BOOST_TYPE: FORTIFICATIONS.STRONGHOLDRESERVE_BOOST,
 REQUISITION_TYPE: FORTIFICATIONS.STRONGHOLDRESERVE_REQUISITION,
 HEAVYTRUCKS_TYPE: FORTIFICATIONS.STRONGHOLDRESERVE_HEAVYTRUCKS}

def getReserveGroupTitle(groupType):
    return i18n.makeString(__locTypeMap[groupType])


def makeReserveSlotTooltipVO(reserve, groupType, empty, havePermissions, isInBattle, disabledByRequisition):
    if reserve is None:
        tooltipType = TOOLTIPS_CONSTANTS.COMPLEX
        header = getReserveGroupTitle(groupType)
        rShortCut = R.strings.fortifications.reserves.tooltip
        if havePermissions:
            if disabledByRequisition:
                description = backport.text(rShortCut.disabledRequisition())
            elif isInBattle:
                description = backport.text(rShortCut.disabledInBattle())
            elif empty:
                description = backport.text(rShortCut.empty())
            else:
                description = backport.text(rShortCut.withPermission())
        else:
            description = backport.text(rShortCut.withoutPermission())
    else:
        header = reserve.getTitle()
        description = reserve.getDescription()
        tooltipType = geReserveTooltipType(reserve.getType())
    return (makeTooltip(header, description), tooltipType)


__typeMapVO = {ARTILLERY_STRIKE: 'artillerySupport',
 REQUISITION: 'requisition',
 HIGH_CAPACITY_TRANSPORT: 'heavyTrucks',
 INSPIRATION: 'inspire'}
__reserveTooltipMap = {ARTILLERY_STRIKE: TOOLTIPS_CONSTANTS.RESERVE_MODULE,
 REQUISITION: TOOLTIPS_CONSTANTS.OLD_RESERVE_MODULE,
 HIGH_CAPACITY_TRANSPORT: TOOLTIPS_CONSTANTS.OLD_RESERVE_MODULE,
 INSPIRATION: TOOLTIPS_CONSTANTS.RESERVE_MODULE}

def getReserveNameVO(name):
    return __typeMapVO.get(name, None)


def geReserveTooltipType(name):
    return __reserveTooltipMap.get(name, None)


def makeReserveModuleData(mID, moduleType, level, count, isSelected, showExtendedParams, paramsItems):
    return {'id': mID,
     'moduleLabel': getReserveNameVO(moduleType),
     'level': level,
     'count': count,
     'isSelected': isSelected,
     'showExtendedParams': showExtendedParams,
     'paramsItems': paramsItems,
     'tooltipType': geReserveTooltipType(moduleType)}


def makeFortClanBattleRoomVO(mapId, headerDescr, mineClanName, enemyClanName, waitForBattleDescr, isMapEnabled, isBattleTimerVisible, isSortie):
    timerVisible = isBattleTimerVisible and not isSortie
    mapName = getArenaShortName(mapId) if mapId else i18n.makeString(FORTIFICATIONS.STRONGHOLDMAP_RANDOMMAP)
    if mapId == 0:
        isMapEnabled = False
    return {'mapID': mapId,
     'mapName': mapName,
     'headerDescr': headerDescr,
     'mineClanName': mineClanName,
     'enemyClanName': enemyClanName,
     'waitForBattleDescr': waitForBattleDescr,
     'isMapEnabled': isMapEnabled,
     'isBattleTimerVisible': timerVisible,
     'isBattleType': not isSortie,
     'teamHeader': i18n.makeString(FORTIFICATIONS.STRONGHOLD_TEAMHEADER)}


def makeClanBattleTimerVO(deltaTime, htmlFormatter, alertHtmlFormatter, glowColor, alertGlowColor, timerDefaultValue, hintState):
    return {'deltaTime': deltaTime,
     'htmlFormatter': htmlFormatter,
     'alertHtmlFormatter': alertHtmlFormatter,
     'glowColor': glowColor,
     'alertGlowColor': alertGlowColor,
     'timerDefaultValue': timerDefaultValue,
     'state': hintState}


__attack = ('attack1', 'attack2', 'attack3', 'attack4', 'attack5')
__defense = ('defense1', 'defense2', 'defense3', 'defense4', 'defense5')

def makeDirectionVO(buildIdx, isAttack, battleIdx):
    if buildIdx is None:
        return 'definition'
    else:
        isSecondBattle = battleIdx == 1
        if isSecondBattle:
            if isAttack:
                return 'attack0'
            return 'defense0'
        size = len(__defense)
        return __attack[buildIdx - 1] if isAttack else __defense[size - buildIdx - 1]


def makeOpenRoomButtonVO(isOpen):
    if isOpen:
        label, stateString, tooltipString = i18n.makeString(FORTIFICATIONS.STRONGHOLDBUTTONS_MAKEINVISIBLE), i18n.makeString(FORTIFICATIONS.STRONGHOLDBUTTONS_MAKEINVISIBLESTATUS), i18n.makeString(TOOLTIPS.FORTIFICATION_UNIT_ACCESS_BODYOPEN)
    else:
        label, stateString, tooltipString = i18n.makeString(FORTIFICATIONS.STRONGHOLDBUTTONS_MAKEVISIBLE), i18n.makeString(FORTIFICATIONS.STRONGHOLDBUTTONS_MAKEVISIBLESTATUS), i18n.makeString(TOOLTIPS.FORTIFICATION_UNIT_ACCESS_BODYCLOSED)
    return (label, stateString, tooltipString)


def makeConfigureButtonVO(isEnabled, isRoomStatusEnabled):
    return {'isEnabled': isEnabled,
     'isRoomStatusEnabled': isRoomStatusEnabled}


def makeTableHeaderVO(currentPlayerCount, maxPlayerCount, currentLegCount, maxLegCount):
    total = i18n.makeString(FORTIFICATIONS.SORTIE_LISTVIEW_TEAMMEMBERS, current=str(currentPlayerCount), max=str(maxPlayerCount))
    legionariesIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_LEGIONNAIRE, 16, 16, -4, 0)
    label = total + ' (' + legionariesIcon + ' ' + str(currentLegCount) + ' / ' + str(maxLegCount) + ')'
    return [{'buttonWidth': 212,
      'buttonHeight': 40,
      'sortOrder': 0,
      'toolTip': '-',
      'defaultSortDirection': 'ascending',
      'label': label,
      'showSeparator': True,
      'textAlign': 'left'}, {'buttonWidth': 67,
      'buttonHeight': 40,
      'sortOrder': 0,
      'toolTip': '-',
      'defaultSortDirection': 'ascending',
      'label': i18n.makeString(FORTIFICATIONS.STRONGHOLDTABLE_RATING),
      'showSeparator': True}, {'buttonWidth': 216,
      'buttonHeight': 40,
      'sortOrder': 0,
      'toolTip': '-',
      'defaultSortDirection': 'ascending',
      'label': i18n.makeString(FORTIFICATIONS.STRONGHOLDTABLE_TECH),
      'showSeparator': False}]


def getDirection(direction):
    return i18n.makeString(FORTIFICATIONS.getDirection(direction) or direction)
