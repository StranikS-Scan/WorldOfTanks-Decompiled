# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wgnc/WGNCPollWindow.py
from adisp import process
from gui import DialogsInterface
from gui.shared import events, EVENT_BUS_SCOPE
from gui.wgnc import g_wgncProvider
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.WGNCPollWindowMeta import WGNCPollWindowMeta

class WGNCPollWindow(WGNCPollWindowMeta):

    def __init__(self, ctx = None):
        super(WGNCPollWindow, self).__init__()
        raise ctx or AssertionError('Context can be defined')
        self.__notID = ctx['notID']
        self.__target = ctx['target']

    @process
    def onWindowClose(self):
        isOk = yield DialogsInterface.showI18nConfirmDialog('interviewQuit', focusedID=DIALOG_BUTTON_ID.SUBMIT)
        if isOk:
            item = g_wgncProvider.getNotItemByName(self.__notID, self.__target)
            if not item:
                return
            button = item.getCancelButton()
            if not button:
                return
            g_wgncProvider.doAction(self.__notID, button.action, self.__target)
            self.destroy()

    def onBtnClick(self):
        item = g_wgncProvider.getNotItemByName(self.__notID, self.__target)
        if not item:
            self.destroy()
            return
        button = item.getSubmitButton()
        if button:
            g_wgncProvider.doAction(self.__notID, button.action, self.__target)
        self.destroy()

    def onLinkClick(self, actions):
        g_wgncProvider.doAction(self.__notID, actions, self.__target)

    def _populate(self):
        super(WGNCPollWindow, self)._populate()
        self.addListener(events.WGNCShowItemEvent.CLOSE_POLL_WINDOW, self.__handlePollWindowClose, EVENT_BUS_SCOPE.LOBBY)
        self.__populateData()

    def _dispose(self):
        self.removeListener(events.WGNCShowItemEvent.CLOSE_POLL_WINDOW, self.__handlePollWindowClose, EVENT_BUS_SCOPE.LOBBY)
        super(WGNCPollWindow, self)._dispose()

    def __populateData(self):
        item = g_wgncProvider.getNotItemByName(self.__notID, self.__target)
        if not item:
            return
        self.as_setWindowTitleS(item.getTopic())
        self.as_setTextS(item.getBody())
        button = item.getSubmitButton()
        if button:
            self.as_setButtonLblS(button.label)

    def __handlePollWindowClose(self, event):
        if self.__notID == event.getNotID() and self.__target == event.getTarget():
            self.destroy()
