# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/notify_center/NotifyCenterDialog.py
from gui.Scaleform.daapi.view.meta.NotifyCenterDialogMeta import NotifyCenterDialogMeta
from gui.notify_center import g_notifyCenterProvider

class NotifyCenterDialog(NotifyCenterDialogMeta):

    def __init__(self, ctx=None):
        super(NotifyCenterDialog, self).__init__()
        self.__notID = ctx['notID']
        self.__target = ctx['target']

    def onWindowClose(self):
        self.destroy()

    def doAction(self, actionID, isButtonClicked):
        g_notifyCenterProvider.doAction(self.__notID, actionID, self.__target)
        if isButtonClicked:
            self.destroy()

    def _populate(self):
        super(NotifyCenterDialog, self)._populate()
        item = g_notifyCenterProvider.getNotItemByName(self.__notID, self.__target)
        self.as_setTextS(item.getBody())
        self.as_setTitleS(item.getTopic())
        self.as_setButtonsS(item.getButtonsMap())

    def _dispose(self):
        self.__notID = None
        self.__target = None
        super(NotifyCenterDialogMeta, self)._dispose()
        return
