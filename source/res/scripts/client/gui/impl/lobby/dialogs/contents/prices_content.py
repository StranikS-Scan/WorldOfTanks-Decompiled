# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/prices_content.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialog_prices_content_model import DialogPricesContentModel
from gui.impl.lobby.dialogs.dialog_prices_tooltip import DialogPricesTooltip
from gui.impl.pub.dialog_window import DialogContent

class DialogPricesContent(DialogContent):
    __slots__ = ('__valueMainCost', '__iconMainCost', '__labelMainCost', '__valueAdditionalCost', '__iconAdditionalCost', '__labelAdditionalCost', '__totalCost', '__labelTotalCost')

    def __init__(self):
        super(DialogPricesContent, self).__init__(layoutID=R.views.common.dialog_view.components.dialog_prices_content.DialogPricesContent(), viewModelClazz=DialogPricesContentModel)

    @property
    def viewModel(self):
        return super(DialogPricesContent, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == self.viewModel.getTooltipId():
            dialog = DialogPricesTooltip()
            dialog.setData(valueMainCost=self.__valueMainCost, iconMainCost=self.__iconMainCost, labelMainCost=self.__labelMainCost, valueAdditionalCost=self.__valueAdditionalCost, iconAdditionalCost=self.__iconAdditionalCost, labelAdditionalCost=self.__labelAdditionalCost, totalCost=self.__totalCost, labelTotalCost=self.__labelTotalCost)
            return dialog
        else:
            return None

    def setData(self, valueMainCost, iconMainCost, labelMainCost, valueAdditionalCost, iconAdditionalCost, labelAdditionalCost, totalCost, labelTotalCost):
        self.__valueMainCost = valueMainCost
        self.__iconMainCost = iconMainCost
        self.__labelMainCost = labelMainCost
        self.__valueAdditionalCost = valueAdditionalCost
        self.__iconAdditionalCost = iconAdditionalCost
        self.__labelAdditionalCost = labelAdditionalCost
        self.__totalCost = totalCost
        self.__labelTotalCost = labelTotalCost
