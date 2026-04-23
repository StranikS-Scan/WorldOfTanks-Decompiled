# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_money_balance.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.customization.customization_money_balance_model import CustomizationMoneyBalanceModel
from gui.impl.pub import ViewImpl

class CustomizationMoneyBalance(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CustomizationMoneyBalanceModel()
        super(CustomizationMoneyBalance, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CustomizationMoneyBalance, self).getViewModel()
