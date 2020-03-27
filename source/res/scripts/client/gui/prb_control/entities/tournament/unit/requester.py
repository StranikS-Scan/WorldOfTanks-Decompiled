# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/tournament/unit/requester.py
from adisp import process
from debug_utils import LOG_ERROR
from gui.prb_control import settings, prb_getters
from gui.prb_control.entities.base.ctx import PrbCtrlRequestCtx
from gui.prb_control.entities.base.requester import IUnitRequestProcessor
from helpers import dependency
from skeletons.gui.web import IWebController
from soft_exception import SoftException
from gui.wgcg.tournament.contexts import TournamentJoinBattleCtx, TournamentLeaveModeCtx, TournamentMatchmakingInfoCtx, TournamentAssignCtx, TournamentUnassignCtx, TournamentChangeOpenedCtx, TournamentSetVehicleCtx, TournamentSetReadyCtx, TournamentKickPlayerCtx, TournamentBattleQueueCtx, TournamentGiveLeadershipCtx, TournamentSendInvitesCtx, TournamentSetSlotVehicleTypeFilter, TournamentSetSlotVehiclesFilter, TournamentStopPlayersMatchingCtx

class TournamentUnitRequestProcessor(IUnitRequestProcessor):
    clansCtrl = dependency.descriptor(IWebController)

    def init(self):
        REQUEST_TYPE = settings.REQUEST_TYPE
        self.__unitContextRemap = {REQUEST_TYPE.LEAVE: TournamentLeaveModeCtx,
         REQUEST_TYPE.ASSIGN: TournamentAssignCtx,
         REQUEST_TYPE.UNASSIGN: TournamentUnassignCtx,
         REQUEST_TYPE.CHANGE_OPENED: TournamentChangeOpenedCtx,
         REQUEST_TYPE.SET_VEHICLE: TournamentSetVehicleCtx,
         REQUEST_TYPE.SET_PLAYER_STATE: TournamentSetReadyCtx,
         REQUEST_TYPE.KICK: TournamentKickPlayerCtx,
         REQUEST_TYPE.BATTLE_QUEUE: TournamentBattleQueueCtx,
         REQUEST_TYPE.GIVE_LEADERSHIP: TournamentGiveLeadershipCtx,
         REQUEST_TYPE.SEND_INVITE: TournamentSendInvitesCtx,
         REQUEST_TYPE.JOIN: TournamentJoinBattleCtx,
         REQUEST_TYPE.MATCHMAKING_INFO: TournamentMatchmakingInfoCtx,
         REQUEST_TYPE.SET_SLOT_VEHICLE_TYPE_FILTER: TournamentSetSlotVehicleTypeFilter,
         REQUEST_TYPE.SET_SLOT_VEHICLES_FILTER: TournamentSetSlotVehiclesFilter,
         REQUEST_TYPE.STOP_PLAYERS_MATCHING: TournamentStopPlayersMatchingCtx}

    def fini(self):
        self.__unitContextRemap.clear()

    def doRequest(self, ctx, methodName, *args, **kwargs):
        callback = kwargs.pop('callback', None)
        self._sendRequest(ctx, methodName, [], callback, *args, **kwargs)
        return

    def doRequestChain(self, ctx, chain):
        self._sendNextRequest(ctx, chain)

    def doRawRequest(self, methodName, *args, **kwargs):
        raise SoftException('NOT IMPLEMENTED FOR TournamentUnitRequestProcessor')

    @process
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
