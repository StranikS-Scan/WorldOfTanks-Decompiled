# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/gf_notifications_controller.py
import BigWorld
import logging
import Event
from gui.prb_control.entities.listener import IGlobalListener
from functools import partial
from adisp import adisp_process
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
from skeletons.gui.game_control import IGFNotificationsController
_logger = logging.getLogger(__name__)

class GFNotificationsController(IGFNotificationsController, IGlobalListener):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(GFNotificationsController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onBattleQueueStateUpdated = Event.Event(self.__eventManager)
        self.__callbackID = None
        self.__actionOnModeSwitched = None
        return

    def fini(self):
        self.__clear()

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def onLobbyInited(self, event):
        self.startGlobalListening()
        self.__hangarSpace.onSpaceCreate += self.__tryCallAction

    def selectRandomBattle(self, callback):
        dispatcher = g_prbLoader.getDispatcher()
        self.__actionOnModeSwitched = callback
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__callbackID = BigWorld.callback(0, partial(self.__doSelectRandomPrb, dispatcher))
            return

    def onPrbEntitySwitched(self):
        if self.prbEntity is None:
            return False
        else:
            if bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANDOM):
                self.__tryCallAction()
            return

    def onEnqueued(self, queueType, *args):
        self.onBattleQueueStateUpdated()

    def onDequeued(self, queueType, *args):
        self.onBattleQueueStateUpdated()

    def __tryCallAction(self):
        if self.__actionOnModeSwitched:
            self.__actionOnModeSwitched()
            self.__actionOnModeSwitched = None
        return

    @adisp_process
    def __doSelectRandomPrb(self, dispatcher):
        self.__callbackID = None
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        return

    def __clear(self):
        self.stopGlobalListening()
        self.__eventManager.clear()
        self.__hangarSpace.onSpaceCreate -= self.__tryCallAction
        self.__actionOnModeSwitched = None
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return
