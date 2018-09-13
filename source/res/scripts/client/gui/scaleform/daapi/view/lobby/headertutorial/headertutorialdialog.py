# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/headerTutorial/HeaderTutorialDialog.py
import BigWorld
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.HeaderTutorialDialogMeta import HeaderTutorialDialogMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class HeaderTutorialDialog(View, HeaderTutorialDialogMeta, AbstractWindowView, AppRef):

    def __init__(self, meta, handler):
        super(HeaderTutorialDialog, self).__init__()
        self.meta = meta
        self.handler = handler

    def onButtonClick(self, buttonID, isCbSelected):
        self.__callHandler(buttonID, isCbSelected)
        self.destroy()

    def onWindowClose(self):
        self.__callHandler(DIALOG_BUTTON_ID.CLOSE, False)
        self.destroy()

    def _populate(self):
        super(HeaderTutorialDialog, self)._populate()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'submitBtnLabel': self.meta.getButtonLabels()[0]['label'],
         'cancelBtnLabel': self.meta.getButtonLabels()[1]['label']})

    def _dispose(self):
        if self.meta is not None:
            self.meta = None
        self.handler = None
        super(HeaderTutorialDialog, self)._dispose()
        return

    def __callHandler(self, buttonID, isCbSelected):
        if self.handler is not None:
            self.handler(buttonID == DIALOG_BUTTON_ID.SUBMIT, isCbSelected)
        return
