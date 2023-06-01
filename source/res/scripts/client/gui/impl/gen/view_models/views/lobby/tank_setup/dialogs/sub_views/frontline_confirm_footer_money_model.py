# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/sub_views/frontline_confirm_footer_money_model.py
from frameworks.wulf import ViewModel

class FrontlineConfirmFooterMoneyModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FrontlineConfirmFooterMoneyModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def getIsExtendedHeight(self):
        return self._getBool(1)

    def setIsExtendedHeight(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(FrontlineConfirmFooterMoneyModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addBoolProperty('isExtendedHeight', False)
