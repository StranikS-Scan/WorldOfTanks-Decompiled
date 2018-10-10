# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/IconPriceDialog.py
from gui.Scaleform.daapi.view.meta.IconPriceDialogMeta import IconPriceDialogMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from helpers import i18n
from gui.shared.formatters import getItemPricesVO

class IconPriceDialog(IconPriceDialogMeta):

    def _populate(self):
        super(IconPriceDialog, self)._populate()
        self.as_setPriceLabelS(i18n.makeString(DIALOGS.REMOVECONFIRMATIONNOTREMOVABLEMONEY_MESSAGEPRICE))
        itemPrice = self._meta.getMessagePrice()
        pricesVO = getItemPricesVO(itemPrice)
        self.as_setMessagePriceS({'itemPrices': pricesVO,
         'actionPrice': self._meta.getAction()})
