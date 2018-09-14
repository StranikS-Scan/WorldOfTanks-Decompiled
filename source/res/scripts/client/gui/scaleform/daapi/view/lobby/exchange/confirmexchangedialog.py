# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/exchange/ConfirmExchangeDialog.py
from adisp import process
from gui import SystemMessages
from gui.Scaleform.daapi.view.meta.ConfirmExchangeDialogMeta import ConfirmExchangeDialogMeta

class ConfirmExchangeDialog(ConfirmExchangeDialogMeta):

    def __init__(self, meta, handler):
        super(ConfirmExchangeDialog, self).__init__()
        self.handler = handler
        self.__setMeta(meta)

    def updateDialog(self, meta, handler):
        if self.handler is not None:
            self._callHandler(False)
        self.handler = handler
        self.__removeMeta()
        self.__setMeta(meta)
        self.__prepareAndSendData()
        return

    def onWindowClose(self):
        self._callHandler(False)
        self.destroy()

    @process
    def exchange(self, goldValue):
        exchangedValue = goldValue * self.meta.getExchangeRate()
        result = yield self.meta.submit(goldValue, exchangedValue)
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self._callHandler(True, self.meta.getTypeCompDescr())
            self.destroy()

    def _populate(self):
        super(ConfirmExchangeDialog, self)._populate()
        self.__prepareAndSendData()

    def _dispose(self):
        self.__removeMeta()
        self.handler = None
        super(ConfirmExchangeDialog, self)._dispose()
        return

    def _callHandler(self, success, *kwargs):
        if self.handler is not None:
            self.handler((success, kwargs))
        return

    def __removeMeta(self):
        if self.meta is not None:
            self.meta.onInvalidate -= self.__prepareAndSendData
            self.meta.onCloseDialog -= self.onWindowClose
            self.meta.destroy()
            self.meta = None
        return

    def __setMeta(self, meta):
        self.meta = meta
        self.meta.onInvalidate += self.__prepareAndSendData
        self.meta.onCloseDialog += self.onWindowClose

    def __prepareAndSendData(self, *args):
        self.as_updateS(self.meta.makeVO())
