# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/dialogs/buy_package_dialog.py
from festivity.festival.constants import FestSyncDataKeys
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_buy_package_confirm_bottom_model import FestivalBuyPackageConfirmBottomModel
from gui.impl.gen.view_models.views.lobby.festival.festival_buy_package_confirm_main_model import FestivalBuyPackageConfirmMainModel
from gui.impl.pub.dialog_window import DialogContent, DialogButtons, DialogWindow
from helpers import dependency
from skeletons.festival import IFestivalController

class BuyPackageDialogWindow(DialogWindow):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__packageItem',)

    def __init__(self, packageItem, parent=None):
        super(BuyPackageDialogWindow, self).__init__(bottomContent=DialogContent(R.views.lobby.festival.festival_buy_package.FestivalBuyPackageBottomContent(), FestivalBuyPackageConfirmBottomModel), content=DialogContent(R.views.lobby.festival.festival_buy_package.FestivalBuyPackageMainContent(), FestivalBuyPackageConfirmMainModel), parent=parent, enableBlur=True, enableBlur3dScene=False)
        self.__packageItem = packageItem

    def _initialize(self):
        super(BuyPackageDialogWindow, self)._initialize()
        with self.viewModel.transaction() as model:
            self.__setMainContent()
            self.__setBottomContent(model)
            self._addButton(DialogButtons.PURCHASE, R.strings.festival.dialogs.buyPackage.button.buy(), isFocused=True, soundDown=R.sounds.shop_buy_button())
            self._addButton(DialogButtons.CANCEL, R.strings.festival.dialogs.buyPackage.button.cancel(), invalidateAll=True)
        self.bottomContentViewModel.onCounterChanged += self.__counterChanged
        self.__festController.onDataUpdated += self.__onUpdated

    def _finalize(self):
        self.bottomContentViewModel.onCounterChanged -= self.__counterChanged
        self.__festController.onDataUpdated -= self.__onUpdated
        super(BuyPackageDialogWindow, self)._finalize()

    def _getResultData(self):
        return self.bottomContentViewModel.getSelectedCounter()

    def __counterChanged(self, eventData):
        counterValue = eventData.get('counter', 0)
        price = self.__packageItem.price * counterValue
        self.bottomContentViewModel.setPrice(price)
        self.__updateBottomContent()

    def __setMainContent(self):
        firstItem = self.__packageItem.extractedItems[0]
        mainContent = self.contentViewModel
        mainContent.setItemTypeName(firstItem.shortUserType)
        mainContent.setItemName(firstItem.shortName)

    def __setBottomContent(self, model):
        bottomContent = model.getBottomContent().getViewModel()
        bottomContent.setPrice(self.__packageItem.price)
        bottomContent.setIsCounterVisible(self.__packageItem.isMultipleAllowed)

    def __updateBottomContent(self):
        price = self.bottomContentViewModel.getPrice()
        tickets = self.__festController.getTickets()
        isMoneyEnough = tickets >= price
        self.bottomContentViewModel.setIsMoneyEnough(isMoneyEnough)
        self._setButtonEnabled(DialogButtons.PURCHASE, isMoneyEnough)

    def __onUpdated(self, keys):
        if FestSyncDataKeys.TICKETS in keys:
            self.__updateBottomContent()
