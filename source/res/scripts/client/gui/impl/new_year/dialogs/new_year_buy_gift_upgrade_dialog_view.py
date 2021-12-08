# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/dialogs/new_year_buy_gift_upgrade_dialog_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.new_year_gift_upgrade_dialog_model import NewYearGiftUpgradeDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView

class NewYearBuyGiftUpgradeDialogView(FullScreenDialogView):
    __slots__ = ('__cost', '__level', '__tokensCount', '__shortage')

    def __init__(self, level, cost, shortage, tokensCount):
        settings = ViewSettings(layoutID=R.views.lobby.new_year.NewYearGiftLevelUp(), model=NewYearGiftUpgradeDialogModel())
        self.__level = level
        self.__cost = cost
        self.__tokensCount = tokensCount
        self.__shortage = shortage
        super(NewYearBuyGiftUpgradeDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _setBaseParams(self, model):
        super(NewYearBuyGiftUpgradeDialogView, self)._setBaseParams(model)
        model.setLevel(self.__level)
        model.setCost(self.__cost)
        model.setTokensCount(self.__tokensCount)
        model.setShortage(self.__shortage)
