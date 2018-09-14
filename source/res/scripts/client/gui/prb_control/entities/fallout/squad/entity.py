# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/squad/entity.py
from UnitBase import ROSTER_TYPE
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control import settings
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.fallout.squad.actions_handler import FalloutSquadActionsHandler
from gui.prb_control.entities.fallout.squad.actions_validator import FalloutSquadActionsValidator
from gui.prb_control.entities.fallout.squad.ctx import ChangeFalloutQueueTypeCtx
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG
_PAN = settings.PREBATTLE_ACTION_NAME
_RT = settings.REQUEST_TYPE
_FF = settings.FUNCTIONAL_FLAG

class FalloutSquadEntryPoint(SquadEntryPoint):

    def __init__(self, queueType, accountsToInvite=None):
        super(FalloutSquadEntryPoint, self).__init__(_FF.FALLOUT, accountsToInvite=accountsToInvite)
        self.__queueType = queueType

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.FALLOUT, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createFalloutSquad(self.__queueType)


class FalloutSquadEntity(SquadEntity):

    def __init__(self):
        super(FalloutSquadEntity, self).__init__(_FF.FALLOUT, PREBATTLE_TYPE.FALLOUT)

    def getQueueType(self):
        rosterType = self.getRosterType()
        if rosterType == ROSTER_TYPE.FALLOUT_CLASSIC_ROSTER:
            return QUEUE_TYPE.FALLOUT_CLASSIC
        return QUEUE_TYPE.FALLOUT_MULTITEAM if rosterType == ROSTER_TYPE.FALLOUT_MULTITEAM_ROSTER else super(FalloutSquadEntity, self).getQueueType()

    def doSelectAction(self, action):
        name = action.actionName
        if name == _PAN.SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        if name == _PAN.FALLOUT:
            g_eventDispatcher.showFalloutWindow()
            return SelectResult(True)
        if name in (_PAN.FALLOUT_CLASSIC, _PAN.FALLOUT_MULTITEAM):
            rosterType = self.getRosterType()
            if name == _PAN.FALLOUT_CLASSIC and rosterType != ROSTER_TYPE.FALLOUT_CLASSIC_ROSTER:
                ctx = ChangeFalloutQueueTypeCtx(QUEUE_TYPE.FALLOUT_CLASSIC, 'prebattle/change_settings')
                self.changeFalloutQueueType(ctx)
            if name == _PAN.FALLOUT_MULTITEAM and rosterType != ROSTER_TYPE.FALLOUT_MULTITEAM_ROSTER:
                ctx = ChangeFalloutQueueTypeCtx(QUEUE_TYPE.FALLOUT_MULTITEAM, 'prebattle/change_settings')
                self.changeFalloutQueueType(ctx)
            return SelectResult(True)
        return super(FalloutSquadEntity, self).doSelectAction(action)

    def changeFalloutQueueType(self, ctx, callback=None):
        battleType = ctx.getBattleType()
        if battleType not in QUEUE_TYPE.FALLOUT:
            LOG_ERROR('Incorrect value of battle type', battleType)
            if callback:
                callback(False)
            return
        if self._isInCoolDown(_RT.CHANGE_FALLOUT_QUEUE_TYPE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change battle type', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'changeFalloutType', newQueueType=battleType)
        self._cooldown.process(_RT.CHANGE_FALLOUT_QUEUE_TYPE, coolDown=ctx.getCooldown())

    def _getRequestHandlers(self):
        handlers = super(FalloutSquadEntity, self)._getRequestHandlers()
        handlers.update({_RT.CHANGE_FALLOUT_QUEUE_TYPE: self.changeFalloutQueueType})
        return handlers

    def _createActionsHandler(self):
        return FalloutSquadActionsHandler(self)

    def _createActionsValidator(self):
        return FalloutSquadActionsValidator(self)
