# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wgnc/WGNCDialog.py
from gui.Scaleform.daapi.view.meta.WGNCDialogMeta import WGNCDialogMeta
from gui.wgnc import g_wgncProvider

class WGNCDialog(WGNCDialogMeta):

    def __init__(self, ctx=None):
        super(WGNCDialog, self).__init__()
        assert ctx, 'Context can be defined'
        self.__notID = ctx['notID']
        self.__target = ctx['target']

    def onWindowClose(self):
        self.destroy()

    def doAction(self, actionID, isButtonClicked):
        g_wgncProvider.doAction(self.__notID, actionID, self.__target)
        if isButtonClicked:
            self.destroy()

    def _populate(self):
        super(WGNCDialog, self)._populate()
        item = g_wgncProvider.getNotItemByName(self.__notID, self.__target)
        self.as_setTextS(item.getBody())
        self.as_setTitleS(item.getTopic())
        self.as_setButtonsS(item.getButtonsMap())

    def _dispose(self):
        self.__notID = None
        self.__target = None
        super(WGNCDialogMeta, self)._dispose()
        return
