# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCQueueDialog.py
import BigWorld
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LoadViewEvent, BCLoginEvent
from gui.Scaleform.daapi.view.meta.BCQueueWindowMeta import BCQueueWindowMeta
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
HIDE_GAME_LOADING_TIMEOUT = 10

class BCQueueDialog(BCQueueWindowMeta):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, settings):
        super(BCQueueDialog, self).__init__()
        self.__backgroundImage = settings['backgroundImage']
        self.__lessonNumber = settings['lessonNumber']
        self.__timeoutTime = settings['timeout']
        self.__startTime = BigWorld.time()
        self.__cancelCallbackId = None
        self.__hideGameLoadingCallbackId = None
        return

    def updateSettings(self, settings):
        if self.__cancelCallbackId:
            BigWorld.cancelCallback(self.__cancelCallbackId)
            self.__cancelCallbackId = None
        if self.__hideGameLoadingCallbackId:
            BigWorld.cancelCallback(self.__hideGameLoadingCallbackId)
            self.__hideGameLoadingCallbackId = None
        self.__backgroundImage = settings['backgroundImage']
        self.__lessonNumber = settings['lessonNumber']
        self.__timeoutTime = settings['timeout']
        self.applyData()
        timeLeft = self.__timeoutTime - BigWorld.time() + self.__startTime
        if timeLeft > 0:
            self.__cancelCallbackId = BigWorld.callback(timeLeft, self.showCancel)
            self.as_showCancelButtonS(False, '', '')
        else:
            self.showCancel()
        self.__hideGameLoadingCallbackId = BigWorld.callback(HIDE_GAME_LOADING_TIMEOUT, self.__hideGameLoading)
        return

    def showCancel(self):
        self.__cancelCallbackId = None
        skipText = BOOTCAMP.QUEUE_CANCEL_QUEUE
        if self.__lessonNumber == 0:
            skipText = BOOTCAMP.QUEUE_SKIP_TUTORIAL
        self.as_showCancelButtonS(True, skipText, BOOTCAMP.QUEUE_QUEUE_TOO_LONG)
        return

    def onWindowClose(self):
        self.cancel()

    def cancel(self):
        g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG_CANCEL)), EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def applyData(self):
        data = {'showTutorialPages': False,
         'backgroundImage': self.__backgroundImage}
        self.as_setDataS(data)
        self.as_setStatusTextS(BOOTCAMP.QUEUE_TITLE)

    def _populate(self):
        super(BCQueueDialog, self)._populate()
        self.connectionMgr.onDisconnected += self.__cm_onDisconnected
        self.__cancelCallbackId = BigWorld.callback(self.__timeoutTime, self.showCancel)
        self.__hideGameLoadingCallbackId = BigWorld.callback(HIDE_GAME_LOADING_TIMEOUT, self.__hideGameLoading)
        self.applyData()

    def _dispose(self):
        if self.__cancelCallbackId is not None:
            BigWorld.cancelCallback(self.__cancelCallbackId)
            self.__cancelCallbackId = None
        if self.__hideGameLoadingCallbackId is not None:
            BigWorld.cancelCallback(self.__hideGameLoadingCallbackId)
            self.__hideGameLoadingCallbackId = None
        self.connectionMgr.onDisconnected -= self.__cm_onDisconnected
        super(BCQueueDialog, self)._dispose()
        return

    def __hideGameLoading(self):
        self.__hideGameLoadingCallbackId = None
        self.fireEvent(BCLoginEvent(BCLoginEvent.HIDE_GAME_LOADING), EVENT_BUS_SCOPE.LOBBY)
        return

    def __handleHideDialog(self, _):
        self.destroy()

    def __cm_onDisconnected(self):
        self.destroy()
