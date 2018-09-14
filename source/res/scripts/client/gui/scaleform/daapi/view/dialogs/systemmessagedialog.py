# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/SystemMessageDialog.py
from gui.Scaleform.daapi.view.meta.SystemMessageDialogMeta import SystemMessageDialogMeta

class SystemMessageDialog(SystemMessageDialogMeta):

    def __init__(self, meta, handler):
        super(SystemMessageDialog, self).__init__()
        self.__meta = meta
        self.__handler = handler

    def _populate(self):
        super(SystemMessageDialog, self)._populate()
        self.as_setInitDataS({'title': self.__meta.getTitle(),
         'closeBtnTitle': self.__meta.getCancelLabel(),
         'settings': self.__meta.getSettings()})
        self.as_setMessageDataS(self.__meta.getMessageObject())

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        if self.__handler:
            self.__handler(True)
        self.__meta.cleanUp()
        self.__meta = None
        self.__handler = None
        super(SystemMessageDialog, self)._dispose()
        return
