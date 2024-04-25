# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/platoon/platoon_helpers.py
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import MAX_PLAYER_COUNT_ALL, makePlayerVO, makeVehicleVO, makeBattleRoyaleSlotLabel, makeSlotLabel, getSquadPlayerStatus, getPlayerStatus, makeUnitRosterConditions
from gui.prb_control import settings
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.prb_control.entities.base.unit.entity import UnitEntity
from historical_battles.gui.impl.gen.view_models.views.common.base_team_member_model import TeamMemberRoleType
from historical_battles_common.hb_constants_extension import INVALID_FRONTMAN_ROLE_ID
from historical_battles_common.hb_constants import FrontmanRoleID
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_slot_model import FrontmanRole
from helpers import dependency
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.storage import storage_getter
from skeletons.gui.shared import IItemsCache
FrontmanRoleIDToRole = {FrontmanRoleID.AVIATION: FrontmanRole.AVIATION,
 FrontmanRoleID.ARTILLERY: FrontmanRole.ARTILLERY,
 FrontmanRoleID.ENGINEER: FrontmanRole.ENGINEER}
FrontmanRoleIDToTeamMemberRole = {FrontmanRoleID.AVIATION: TeamMemberRoleType.AVIATION,
 FrontmanRoleID.ARTILLERY: TeamMemberRoleType.ARTILLERY,
 FrontmanRoleID.ENGINEER: TeamMemberRoleType.ENGINEER}

def getPlatoonSlotsData(unitEntity):
    orderedSlots = []
    if isinstance(unitEntity, UnitEntity):
        unitFullData = unitEntity.getUnitFullData(unitEntity.getID())
        if unitFullData.unit is None:
            return orderedSlots
        _, slots = makeSlotsVOs(unitEntity, unitEntity.getID(), withPrem=True)
        orderedSlots = sorted(slots, key=lambda item: bool(item.get('player')), reverse=True)
    return orderedSlots


def makeSlotsVOs(unitEntity, unitMgrID=None, maxPlayerCount=MAX_PLAYER_COUNT_ALL, withPrem=False):
    fullData = unitEntity.getUnitFullData(unitMgrID=unitMgrID)
    if fullData is None or fullData.unit is None:
        return (False, {})
    else:
        slots = _getSlotsData(unitMgrID, fullData, unitEntity.getRosterSettings().getLevelsRange(), maxPlayerCount=maxPlayerCount, withPrem=withPrem)
        isRosterSet = fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES)
        return (isRosterSet, slots)


def getCommanderInfo(unitEntity, unitMgrID=None):
    fullData = unitEntity.getUnitFullData(unitMgrID=unitMgrID)
    for slotInfo in fullData.slotsIterator:
        if slotInfo.player is not None and slotInfo.player.isCommander():
            return slotInfo

    return {}


def _getSlotsData(unitMgrID, fullData, levelsRange=None, checkForVehicles=True, maxPlayerCount=MAX_PLAYER_COUNT_ALL, withPrem=False):
    pInfo = fullData.playerInfo
    isPlayerCreator = pInfo.isCommander()
    isPlayerInSlot = pInfo.isInSlot
    slots = []
    userGetter = storage_getter('users')().getUser
    colorGetter = g_settings.getColorScheme('rosters').getColors
    itemsCache = dependency.instance(IItemsCache)
    vehicleGetter = itemsCache.items.getItemByCD
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
         'isEvent': True,
         'rating': rating,
         'isLegionaries': isLegionaries,
         'isLocked': isLocked,
         'role': role}
        if withPrem:
            slot['hasPremiumAccount'] = player and player.hasPremium
        slot.update({'isVisibleAdtMsg': False,
         'additionalMsg': ''})
        if player is not None and player.isReady:
            eventEnqueueData = player.extraData.get('eventEnqueueData', {})
            roleID = eventEnqueueData.get('roleID', INVALID_FRONTMAN_ROLE_ID)
            role = FrontmanRoleIDToRole.get(roleID, FrontmanRole.NONE)
            speciality = R.strings.hb_lobby.memberWindow.speciality
            slot.update({'speciality': role,
             'specialityTooltipHead': backport.text(speciality.head.dyn(role.value)()) if role else '',
             'specialityTooltipBody': backport.text(speciality.body.dyn(role.value)()) if role else ''})
        slots.append(slot)
        playerCount += 1

    return slots
