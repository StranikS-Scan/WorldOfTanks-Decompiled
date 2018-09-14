# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/PrequeueWindow.py
from adisp import process
from CurrentVehicle import g_currentVehicle
from gui.prb_control.context import pre_queue_ctx
from gui.shared import events, EVENT_BUS_SCOPE
from gui.prb_control.prb_helpers import QueueListener
from gui.Scaleform.daapi.view.meta.PrequeueWindowMeta import PrequeueWindowMeta
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS

@stored_window(DATA_TYPE.CAROUSEL_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class PrequeueWindow(PrequeueWindowMeta, QueueListener):

    def __init__(self, queueName = 'prequeue'):
        super(PrequeueWindow, self).__init__()
        self.__queueName = queueName

    def onWindowClose(self):
        self.destroy()

    def onWindowMinimize(self):
        self.destroy()

    def requestToEnqueue(self):
        self.preQueueFunctional.doAction()

    @process
    def requestToLeave(self):
        yield self.prbDispatcher.leave(pre_queue_ctx.LeavePreQueueCtx(waitingID='prebattle/leave'))

    def showFAQWindow(self):
        self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.FAQ_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def isEnqueueBtnEnabled(self):
        return g_currentVehicle.isReadyToPrebattle() and not self.preQueueFunctional.isInQueue()

    def isLeaveBtnEnabled(self):
        return not self.preQueueFunctional.isInQueue()

    def startListening(self):
        self.startQueueListening()
        g_currentVehicle.onChanged += self._handleCurrentVehicleChanged

    def stopListening(self):
        self.stopQueueListening()
        g_currentVehicle.onChanged -= self._handleCurrentVehicleChanged

    def _populate(self):
        super(PrequeueWindow, self)._populate()
        self.startListening()
        self.as_enableEnqueueBtnS(self.isEnqueueBtnEnabled())

    def _dispose(self):
        self.stopListening()
        super(PrequeueWindow, self)._dispose()

    def _handleCurrentVehicleChanged(self):
        self.as_enableEnqueueBtnS(self.isEnqueueBtnEnabled())
