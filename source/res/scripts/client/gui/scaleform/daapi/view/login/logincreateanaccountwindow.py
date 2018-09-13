# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/LoginCreateAnAccountWindow.py
from gui.Scaleform.daapi.view.meta.LoginCreateAnAccountWindowMeta import LoginCreateAnAccountWindowMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
import BigWorld
import ResMgr
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LoginEvent, LoginCreateEvent
__author__ = 'd_trofimov'

class LoginCreateAnAccountWindow(View, AbstractWindowView, LoginCreateAnAccountWindowMeta, AppRef):

    def __init__(self, title, message, submitLabel):
        super(LoginCreateAnAccountWindow, self).__init__()
        self.__title = title
        self.__message = message
        self.__submitLabel = submitLabel

    def _populate(self):
        super(LoginCreateAnAccountWindow, self)._populate()
        self.as_updateTextsS('', self.__title, self.__message, self.__submitLabel)
        self.addListener(LoginEvent.CLOSE_CREATE_AN_ACCOUNT, self.__onCreateAccResponse)

    def onWindowClose(self):
        self.destroy()

    def onRegister(self, nickname):
        self.fireEvent(LoginCreateEvent(LoginCreateEvent.CREATE_AN_ACCOUNT_REQUEST, View.alias, self.__title, nickname, self.__submitLabel), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(LoginEvent.CLOSE_CREATE_AN_ACCOUNT, self.__onCreateAccResponse)
        super(LoginCreateAnAccountWindow, self)._dispose()

    def __onCreateAccResponse(self, event):
        self.as_registerResponseS(event.isSuccess, event.errorMsg)
