# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_piggy_bank_card_model.py
from gui.impl.gen.view_models.views.lobby.premacc.piggybank_base_model import PiggybankBaseModel

class PremDashboardPiggyBankCardModel(PiggybankBaseModel):
    __slots__ = ('onGoToPiggyView',)

    def __init__(self, properties=7, commands=1):
        super(PremDashboardPiggyBankCardModel, self).__init__(properties=properties, commands=commands)

    def getIsAvailable(self):
        return self._getBool(6)

    def setIsAvailable(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(PremDashboardPiggyBankCardModel, self)._initialize()
        self._addBoolProperty('isAvailable', True)
        self.onGoToPiggyView = self._addCommand('onGoToPiggyView')
