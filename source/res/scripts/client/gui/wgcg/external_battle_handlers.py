# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/external_battle_handlers.py
from functools import partial
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType, ExternalBattleStorageName
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager

class BaseExternalBattleUnitRequestHandlers(RequestHandlers):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def get(self):
        handlers = {WebRequestDataType.STRONGHOLD_LEAVE: partial(self.__leave, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_ASSIGN: partial(self.__assign, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_UNASSIGN: partial(self.__unassign, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_CHANGE_OPENED: partial(self.__changeOpened, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SET_VEHICLE: partial(self.__setVehicle, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SET_PLAYER_STATE: partial(self.__setPlayerState, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SEND_INVITE: partial(self.__sendInvite, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_KICK: partial(self.__kick, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_BATTLE_QUEUE: partial(self.__battleQueue, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_GIVE_LEADERSHIP: partial(self.__giveLeadership, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_TAKE_LEADERSHIP: partial(self.__takeLeadership, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SET_RESERVE: partial(self.__setReserve, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_UNSET_RESERVE: partial(self.__unsetReserve, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_UPDATE: partial(self.__updateExternalBattleBase, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_STATISTICS: partial(self.__getExternalBattleUnitStatistics, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_JOIN_BATTLE: partial(self.__joinBattle, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SET_EQUIPMENT_COMMANDER: partial(self.__setEquipmentCommander, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_MATCHMAKING_INFO: partial(self.__matchmakingInfo, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SET_SLOT_VEHICLE_TYPE_FILTER: partial(self.__setSlotVehicleTypeFilter, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SET_SLOT_VEHICLES_FILTER: partial(self.__setSlotVehiclesFilter, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_STOP_PLAYERS_MATCHING: partial(self.__stopPlayersMatching, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_LEAVE_MODE: partial(self.__leaveMode, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.STRONGHOLD_SLOT_VEHICLE_FILTERS_UPDATE: partial(self.__getSlotVehicleFilters, ExternalBattleStorageName.STRONGHOLD),
         WebRequestDataType.TOURNAMENT_LEAVE: partial(self.__leave, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_ASSIGN: partial(self.__assign, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_CHANGE_OPENED: partial(self.__changeOpened, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_SET_VEHICLE: partial(self.__setVehicle, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_SET_PLAYER_STATE: partial(self.__setPlayerState, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_SEND_INVITE: partial(self.__sendInvite, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_KICK: partial(self.__kick, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_BATTLE_QUEUE: partial(self.__battleQueue, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_GIVE_LEADERSHIP: partial(self.__giveLeadership, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_TAKE_LEADERSHIP: partial(self.__takeLeadership, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_UPDATE: partial(self.__updateExternalBattleBase, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_JOIN_BATTLE: partial(self.__joinBattle, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_MATCHMAKING_INFO: partial(self.__matchmakingInfo, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_SET_SLOT_VEHICLE_TYPE_FILTER: partial(self.__setSlotVehicleTypeFilter, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_SLOT_VEHICLE_FILTERS_UPDATE: partial(self.__setSlotVehiclesFilter, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_STOP_PLAYERS_MATCHING: partial(self.__stopPlayersMatching, ExternalBattleStorageName.TOURNAMENT),
         WebRequestDataType.TOURNAMENT_LEAVE_MODE: partial(self.__leaveMode, ExternalBattleStorageName.TOURNAMENT)}
        return handlers

    def __assign(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'assign_player'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getPlayerID(), ctx.getSlotIdx())

    def __unassign(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'unassign_player'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getPlayerID())

    def __changeOpened(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'set_open'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.isOpened())

    def __setVehicle(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'set_vehicle'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getVehTypeCD())

    def __setPlayerState(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'set_readiness'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.isReady(), False)

    def __sendInvite(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'invite_players'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getDatabaseIDs(), ctx.getComment())

    def __kick(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'kick_player'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getPlayerID())

    def __battleQueue(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'set_readiness'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.isRequestToStart(), False)

    def __giveLeadership(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'give_leadership'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getPlayerID())

    def __takeLeadership(self, api, ctx, callback):
        self._requester.doRequestEx(ctx, callback, (api, 'take_away_leadership'), self.__getPeripheryIDStr(), ctx.getUnitMgrID())

    def __setReserve(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'lock_reserve'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getReserveID())

    def __setEquipmentCommander(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'set_equipment_commander'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getPlayerID())

    def __unsetReserve(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'unlock_reserve'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getReserveID())

    def __leave(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'leave_room'), self.__getPeripheryIDStr(), ctx.getUnitMgrID())

    def __leaveMode(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'leave_mode'))

    def __updateExternalBattleBase(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'get_wgsh_unit_info'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getRev())

    def __joinBattle(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'join_room'), self.__getPeripheryIDStr(), ctx.getUnitMgrID())

    def __matchmakingInfo(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'matchmaking_info'), self.__getPeripheryIDStr(), ctx.getUnitMgrID())

    def __setSlotVehicleTypeFilter(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'set_slot_vehicle_type_filter'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getSlotIdx(), ctx.getVehicleTypes())

    def __getSlotVehicleFilters(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'get_slot_vehicle_filters'), self.__getPeripheryIDStr(), ctx.getUnitMgrID())

    def __setSlotVehiclesFilter(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'set_slot_vehicles_filter'), self.__getPeripheryIDStr(), ctx.getUnitMgrID(), ctx.getSlotIdx(), ctx.getVehicles())

    def __stopPlayersMatching(self, api, ctx, callback, *args, **kwargs):
        self._requester.doRequestEx(ctx, callback, (api, 'stop_players_matching'), self.__getPeripheryIDStr(), ctx.getUnitMgrID())

    def __getExternalBattleUnitStatistics(self, api, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, (api, 'clan_statistics'), clan_id=ctx.getClanID())

    def __getPeripheryIDStr(self):
        return str(self.connectionMgr.peripheryID)
