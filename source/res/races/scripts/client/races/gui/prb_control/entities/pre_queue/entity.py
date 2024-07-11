# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/prb_control/entities/pre_queue/entity.py
import logging
import BigWorld
import typing
from races.gui.prb_control.entities.pre_queue.actions_validator import RacesBattleActionsValidator
from races.gui.prb_control.entities.pre_queue.ctx import RacesQueueCtx
from races.gui.prb_control.entities.pre_queue.vehicles_watcher import RacesVehiclesWatcher
from races.gui.prb_control.entities.scheduler import RacesScheduler
from races.gui.prb_control.prb_config import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from races_common.races_constants import QUEUE_TYPE
from CurrentVehicle import g_currentVehicle
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.permissions import IPrbPermissions
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from helpers import dependency
from skeletons.gui.game_control import IRacesBattleController
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.local_storage import LocalStorage
    from typing import Optional
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(ctrl=IRacesBattleController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable() and ctrl.isBattleAvailable()


class RacesPermissions(IPrbPermissions):
    pass


class RacesBattleEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(RacesBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.RACES, QUEUE_TYPE.RACES)


class RacesEntity(PreQueueEntity):
    __racesBattleCtrl = dependency.descriptor(IRacesBattleController)

    def __init__(self):
        super(RacesEntity, self).__init__(FUNCTIONAL_FLAG.RACES, QUEUE_TYPE.RACES, PreQueueSubscriber())
        self.__watcher = None
        return

    @prbDispatcherProperty
    def _prbDispatcher(self):
        return None

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.__watcher = RacesVehiclesWatcher()
        self.__watcher.start()
        self.__racesBattleCtrl.onPrbEnter()
        self._loadHangar()
        result = super(RacesEntity, self).init(ctx)
        return result

    def leave(self, ctx, callback=None):
        super(RacesEntity, self).leave(ctx=ctx, callback=callback)
        self.__racesBattleCtrl.onPrbLeave()

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_eventDispatcher.loadHangar()
        return super(RacesEntity, self).fini(ctx, woEvents)

    def resetPlayerState(self):
        super(RacesEntity, self).resetPlayerState()
        g_eventDispatcher.loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return RacesQueueCtx(invID, waitingID='prebattle/join')

    def getPermissions(self, pID=None, **kwargs):
        return RacesPermissions()

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.RACES else super(RacesEntity, self).doSelectAction(action)

    def _createActionsValidator(self):
        return RacesBattleActionsValidator(self)

    def _createScheduler(self):
        return RacesScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().AccountRacesComponent.enqueue(ctx.getVehicleInventoryID())
        _logger.debug('Sends request on queuing to the Races - %r', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountRacesComponent.dequeue()
        _logger.debug('Sends request on dequeuing from the Races')

    def _goToQueueUI(self):
        self.__racesBattleCtrl.openQueueView()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        uiLoader = dependency.instance(IGuiLoader)
        contentID = R.views.races.lobby.races_queue_view.RacesQueueView()
        view = uiLoader.windowsManager.getViewByLayoutID(contentID)
        if view:
            view.destroy()
        self._loadHangar()

    def _loadHangar(self):
        if self.__racesBattleCtrl.isEnabled and self.__racesBattleCtrl.isBattleAvailable():
            self.__racesBattleCtrl.openEventLobby()
        else:
            g_eventDispatcher.loadHangar()
