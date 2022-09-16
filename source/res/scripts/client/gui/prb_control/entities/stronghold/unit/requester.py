# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/requester.py
from adisp import adisp_process
from debug_utils import LOG_ERROR
from gui.prb_control import settings, prb_getters
from gui.prb_control.entities.base.ctx import PrbCtrlRequestCtx
from gui.prb_control.entities.base.requester import IUnitRequestProcessor
from gui.wgcg.strongholds.contexts import StrongholdLeaveCtx, StrongholdAssignCtx, StrongholdChangeOpenedCtx, StrongholdSetVehicleCtx, StrongholdSetReadyCtx, StrongholdKickPlayerCtx, StrongholdBattleQueueCtx, StrongholdGiveLeadershipCtx, StrongholdSetReserveCtx, StrongholdSendInvitesCtx, StrongholdUnassignCtx, StrongholdUnsetReserveCtx, StrongholdJoinBattleCtx, StrongholdSetEquipmentCommanderCtx, StrongholdMatchmakingInfoCtx, StrongholdSetSlotVehicleTypeFilter, StrongholdStopPlayersMatchingCtx, StrongholdSetSlotVehiclesFilter
from helpers import dependency
from skeletons.gui.web import IWebController
from soft_exception import SoftException

class StrongholdUnitRequestProcessor(IUnitRequestProcessor):
    clansCtrl = dependency.descriptor(IWebController)

    def init(self):
        REQUEST_TYPE = settings.REQUEST_TYPE
        self.__unitContextRemap = {REQUEST_TYPE.LEAVE: StrongholdLeaveCtx,
         REQUEST_TYPE.ASSIGN: StrongholdAssignCtx,
         REQUEST_TYPE.UNASSIGN: StrongholdUnassignCtx,
         REQUEST_TYPE.CHANGE_OPENED: StrongholdChangeOpenedCtx,
         REQUEST_TYPE.SET_VEHICLE: StrongholdSetVehicleCtx,
         REQUEST_TYPE.SET_PLAYER_STATE: StrongholdSetReadyCtx,
         REQUEST_TYPE.KICK: StrongholdKickPlayerCtx,
         REQUEST_TYPE.BATTLE_QUEUE: StrongholdBattleQueueCtx,
         REQUEST_TYPE.GIVE_LEADERSHIP: StrongholdGiveLeadershipCtx,
         REQUEST_TYPE.SET_RESERVE: StrongholdSetReserveCtx,
         REQUEST_TYPE.UNSET_RESERVE: StrongholdUnsetReserveCtx,
         REQUEST_TYPE.SEND_INVITE: StrongholdSendInvitesCtx,
         REQUEST_TYPE.JOIN: StrongholdJoinBattleCtx,
         REQUEST_TYPE.SET_EQUIPMENT_COMMANDER: StrongholdSetEquipmentCommanderCtx,
         REQUEST_TYPE.MATCHMAKING_INFO: StrongholdMatchmakingInfoCtx,
         REQUEST_TYPE.SET_SLOT_VEHICLE_TYPE_FILTER: StrongholdSetSlotVehicleTypeFilter,
         REQUEST_TYPE.SET_SLOT_VEHICLES_FILTER: StrongholdSetSlotVehiclesFilter,
         REQUEST_TYPE.STOP_PLAYERS_MATCHING: StrongholdStopPlayersMatchingCtx}

    def fini(self):
        self.__unitContextRemap.clear()

    def doRequest(self, ctx, methodName, *args, **kwargs):
        callback = kwargs.pop('callback', None)
        self._sendRequest(ctx, methodName, [], callback, *args, **kwargs)
        return

    def doRequestChain(self, ctx, chain):
        self._sendNextRequest(ctx, chain)

    def doRawRequest(self, methodName, *args, **kwargs):
        raise SoftException('NOT IMPLEMENTED FOR StrongholdUnitRequestProcessor')

    @adisp_process
    def _sendRequest(self, ctx, methodName, chain, callback, *args, **kwargs):
        if isinstance(ctx, PrbCtrlRequestCtx):
            requestType = ctx.getRequestType()
            if requestType in self.__unitContextRemap:
                clazz = self.__unitContextRemap[requestType]
                ctx = clazz.fromPrbCtx(ctx, prb_getters.getUnitMgrID())
            else:
                LOG_ERROR('Remaped context not found', ctx)
                callback(False)
        result = yield self.clansCtrl.sendRequest(ctx, allowDelay=True)
        if callable(callback):
            callback(result)
        if ctx is not None:
            if result and chain:
                self._sendNextRequest(ctx, chain)
        return

    def _sendNextRequest(self, ctx, chain):
        methodName, args, kwargs = chain[0]
        return self._sendRequest(ctx, methodName, chain[1:], *args, **kwargs)
