# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/PunishmentDialog.py
from gui.Scaleform.daapi.view.meta.PunishmentDialogMeta import PunishmentDialogMeta

class PunishmentDialog(PunishmentDialogMeta):

    def __init__(self, meta, handler):
        super(PunishmentDialog, self).__init__(meta.getMessage(), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self.__msgTitle = meta.getMsgTitle()

    def _populate(self):
        super(PunishmentDialog, self)._populate()
        self.as_setMsgTitleS(self.__msgTitle)
