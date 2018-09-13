# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/IconPriceDialog.py
import BigWorld
from gui.Scaleform.daapi.view.dialogs.IconDialog import IconDialog
from gui.Scaleform.daapi.view.meta.IconPriceDialogMeta import IconPriceDialogMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from helpers import i18n

class IconPriceDialog(IconPriceDialogMeta, IconDialog):

    def __init__(self, meta, handler):
        IconDialog.__init__(self, meta, handler)
        IconPriceDialogMeta.__init__(self)

    def _populate(self):
        super(IconPriceDialog, self)._populate()
        self.as_setPriceLabelS(i18n.makeString(DIALOGS.REMOVECONFIRMATIONNOTREMOVABLEGOLD_MESSAGEPRICE))
        self.as_setMessagePriceS(self._meta.getMessagePrice(), 'gold', self._meta.getAction())
