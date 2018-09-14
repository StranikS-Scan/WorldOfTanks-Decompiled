# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/CheckBoxDialog.py
from adisp import process
from gui.Scaleform.daapi.view.meta.ConfirmDialogMeta import ConfirmDialogMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View

class CheckBoxDialog(View, ConfirmDialogMeta, AbstractWindowView):

    def __init__(self, meta, handler):
        super(CheckBoxDialog, self).__init__()
        self.meta = meta
        self.handler = handler

    def _callHandler(self, success, selected):
        if self.handler is not None:
            self.handler((success, selected))
        return

    def _populate(self):
        super(CheckBoxDialog, self)._populate()
        buttonLabels = self.meta.getButtonsSubmitCancel()
        self.as_setSettingsS({'title': self.meta.getTitle(),
         'description': self.meta.getMessage(),
         'submitBtnLabel': buttonLabels['submit'],
         'cancelBtnLabel': buttonLabels['cancel'],
         'checkBoxLabel': self.meta.getCheckBoxButtonLabel(),
         'checkBoxSelected': self.meta.getCheckBoxSelected()})

    def _dispose(self):
        if self.meta is not None:
            self.meta = None
        self.handler = self._data = None
        super(CheckBoxDialog, self)._dispose()
        return

    def onWindowClose(self):
        self._callHandler(False, self.meta.getCheckBoxSelected())
        self.destroy()

    def submit(self, selected):
        self._callHandler(True, selected)
        self.destroy()
