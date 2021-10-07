# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/piggy_bank/prem_piggy_bank_card_model.py
from gui.impl.gen.view_models.views.lobby.premacc.piggybank_base_model import PiggybankBaseModel

class PremPiggyBankCardModel(PiggybankBaseModel):
    __slots__ = ('onGoToPiggyView',)

    def __init__(self, properties=8, commands=1):
        super(PremPiggyBankCardModel, self).__init__(properties=properties, commands=commands)

    def getIsAvailable(self):
        return self._getBool(6)

    def setIsAvailable(self, value):
        self._setBool(6, value)

    def getIsGoldReserveAvailable(self):
        return self._getBool(7)

    def setIsGoldReserveAvailable(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(PremPiggyBankCardModel, self)._initialize()
        self._addBoolProperty('isAvailable', True)
        self._addBoolProperty('isGoldReserveAvailable', True)
        self.onGoToPiggyView = self._addCommand('onGoToPiggyView')
