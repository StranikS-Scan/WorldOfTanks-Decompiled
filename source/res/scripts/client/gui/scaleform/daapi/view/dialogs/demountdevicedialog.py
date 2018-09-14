# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/DemountDeviceDialog.py
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs.IconPriceDialog import IconPriceDialog

class DemountDeviceDialog(IconPriceDialog):

    def __init__(self, meta, handler):
        super(IconPriceDialog, self).__init__(meta, handler)
        self._meta.onConfirmationStatusChnaged += self.__confirmationStatusChangeHandler

    def _populate(self):
        super(DemountDeviceDialog, self)._populate()
        self.__confirmationStatusChangeHandler(self._meta.isOperationAllowed)

    def __confirmationStatusChangeHandler(self, isAllowed):
        self.as_setOperationAllowedS(isAllowed)
        self.as_setButtonEnablingS(DIALOG_BUTTON_ID.SUBMIT, isAllowed)
        if not isAllowed:
            self.as_setButtonFocusS(DIALOG_BUTTON_ID.CLOSE)

    def _dispose(self):
        self._meta.onConfirmationStatusChnaged -= self.__confirmationStatusChangeHandler
        self._meta.dispose()
        self._meta = None
        super(IconPriceDialog, self)._dispose()
        return
