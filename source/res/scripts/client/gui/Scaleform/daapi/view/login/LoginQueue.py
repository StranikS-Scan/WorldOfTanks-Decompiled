# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/LoginQueue.py
from gui.Scaleform.daapi.view.meta.LoginQueueWindowMeta import LoginQueueWindowMeta
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LoginEvent, LoginEventEx, ArgsEvent
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager

class LoginQueue(LoginQueueWindowMeta):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, title, message, cancelLabel, showAutoLoginBtn):
        super(LoginQueue, self).__init__()
        self.__updateData(title, message, cancelLabel, showAutoLoginBtn)

    def __updateData(self, title, message, cancelLabel, showAutoLoginBtn):
        self.__title = title
        self.__message = message
        self.__cancelLabel = cancelLabel
        self.__showAutoLoginBtn = showAutoLoginBtn

    def __updateTexts(self):
        self.as_setTitleS(self.__title)
        self.as_setMessageS(self.__message)
        self.as_setCancelLabelS(self.__cancelLabel)
        self.as_showAutoLoginBtnS(self.__showAutoLoginBtn)

    def _populate(self):
        super(LoginQueue, self)._populate()
        self.__updateTexts()
        self.addListener(LoginEvent.CANCEL_LGN_QUEUE, self.__onCancelLoginQueue)
        self.addListener(ArgsEvent.UPDATE_ARGS, self.__onUpdateArgs, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(LoginEvent.CANCEL_LGN_QUEUE, self.__onCancelLoginQueue)
        self.removeListener(ArgsEvent.UPDATE_ARGS, self.__onUpdateArgs, EVENT_BUS_SCOPE.LOBBY)
        super(LoginQueue, self)._dispose()

    def onWindowClose(self):
        self.__windowClosing()

    def onCancelClick(self):
        self.__windowClosing()

    def onAutoLoginClick(self):
        self.fireEvent(LoginEventEx(LoginEventEx.SWITCH_LOGIN_QUEUE_TO_AUTO, '', '', '', '', False), EVENT_BUS_SCOPE.LOBBY)
        self.connectionMgr.disconnect()
        self.destroy()

    def __windowClosing(self):
        self.fireEvent(LoginEventEx(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, '', '', '', '', False), EVENT_BUS_SCOPE.LOBBY)
        self.connectionMgr.disconnect()
        self.destroy()

    def __onCancelLoginQueue(self, event):
        self.destroy()

    def __onUpdateArgs(self, event):
        ctx = event.ctx
        if event.alias == self.getAlias():
            self.__updateData(**ctx)
            self.__updateTexts()
