# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.base.unit.ctx import SetVehicleUnitCtx, SetReadyUnitCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.shared.utils import getPlayerDatabaseID
from gui.shared.utils.decorators import ReprInjector
from gui.prb_control import settings as prb_settings
from helpers import dependency
from gui.prb_control.entities.event.squad.scheduler import EventSquadScheduler
from skeletons.gui.server_events import IEventsCache
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.base import vehicleAmmoCheck

@ReprInjector.withParent()
class EventSquadSettingsCtx(SquadSettingsCtx):
    __slots__ = ('_keepCurrentView',)

    def __init__(self, waitingID='', accountsToInvite=None, keepCurrentView=False):
        super(EventSquadSettingsCtx, self).__init__(PREBATTLE_TYPE.EVENT, waitingID, prb_settings.FUNCTIONAL_FLAG.UNDEFINED, accountsToInvite, False)
        self._keepCurrentView = keepCurrentView

    def getKeepCurrentView(self):
        return self._keepCurrentView


class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT | FUNCTIONAL_FLAG.LOAD_PAGE, accountsToInvite)
        self._keepCurrentView = False

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()

    def setKeepCurrentView(self, keepCurrentView):
        self._keepCurrentView = keepCurrentView

    def makeDefCtx(self):
        return EventSquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=self._accountsToInvite, keepCurrentView=self._keepCurrentView)


class EventBattleSquadEntity(SquadEntity):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        if ctx is not None:
            initCtx = ctx.getInitCtx()
            fromEventSquad = isinstance(initCtx, EventSquadSettingsCtx)
            if not fromEventSquad or not initCtx.getKeepCurrentView():
                if self.getPlayerInfo().isReady and self.getFlags().isInQueue():
                    g_eventDispatcher.loadBattleQueue()
                else:
                    g_eventDispatcher.loadHangar()
        return super(EventBattleSquadEntity, self).init(ctx)

    def getQueueType(self):
        return QUEUE_TYPE.EVENT_BATTLES

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.EVENT_SQUAD, PREBATTLE_ACTION_NAME.EVENT_BATTLE):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(EventBattleSquadEntity, self).doSelectAction(action)

    def getLeaderEventEnqueueData(self):
        selfDBID = getPlayerDatabaseID()
        if self.isCommander(dbID=selfDBID):
            return None
        else:
            unitId, unit = self.getUnit()
            for slot in self.getSlotsIterator(unitId, unit):
                if not slot.player:
                    continue
                dbID = slot.player.dbID
                pInfo = self.getPlayerInfo(dbID=dbID)
                if pInfo.isReady and self.isCommander(dbID=dbID):
                    return pInfo.extraData.get('eventEnqueueData', {})

            return None

    def getConfirmDialogMeta(self, ctx):
        if not self.eventsCache.isEventEnabled():
            self.__showDialog(ctx)
            return None
        else:
            return super(EventBattleSquadEntity, self).getConfirmDialogMeta(ctx)

    @vehicleAmmoCheck
    def togglePlayerReadyAction(self, launchChain=False):
        notReady = not self.getPlayerInfo().isReady
        if notReady:
            waitingID = 'prebattle/player_ready'
        else:
            waitingID = 'prebattle/player_not_ready'
        if launchChain:
            if notReady:
                BigWorld.player().changeEventEnqueueData({})
                selVehCtx = SetVehicleUnitCtx(vTypeCD=g_currentVehicle.item.intCD, waitingID='prebattle/change_settings')
                selVehCtx.setReady = True
                self.setVehicle(selVehCtx)
            else:
                ctx = SetReadyUnitCtx(False, 'prebattle/player_not_ready')
                ctx.resetVehicle = True
                LOG_DEBUG('Unit request', ctx)
                self.setPlayerReady(ctx)
        else:
            ctx = SetReadyUnitCtx(notReady, waitingID)
            LOG_DEBUG('Unit request', ctx)
            self.setPlayerReady(ctx)

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)

    def _createScheduler(self):
        return EventSquadScheduler(self)

    def __showDialog(self, ctx):
        DialogsInterface.showDialog(rally_dialog_meta.createLeaveInfoMeta(ctx, 'eventDisabled'), lambda _: None)
