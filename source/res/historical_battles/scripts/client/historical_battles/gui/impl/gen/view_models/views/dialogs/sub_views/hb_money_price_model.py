# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/dialogs/sub_views/hb_money_price_model.py
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.common.multi_price_view_model import MultiPriceViewModel
from gui.impl.gen.view_models.views.dialogs.dialog_base_focus_view_model import DialogBaseFocusViewModel

class HbMoneyPriceModel(MultiPriceViewModel):
    __slots__ = ('onStepperValueChanged',)

    def __init__(self, properties=4, commands=1):
        super(HbMoneyPriceModel, self).__init__(properties=properties, commands=commands)

    @property
    def focus(self):
        return self._getViewModel(1)

    @staticmethod
    def getFocusType():
        return DialogBaseFocusViewModel

    def getText(self):
        return self._getResource(2)

    def setText(self, value):
        self._setResource(2, value)

    def getStepperMaxValue(self):
        return self._getNumber(3)

    def setStepperMaxValue(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(HbMoneyPriceModel, self)._initialize()
        self._addViewModelProperty('focus', DialogBaseFocusViewModel())
        self._addResourceProperty('text', R.invalid())
        self._addNumberProperty('stepperMaxValue', 0)
        self.onStepperValueChanged = self._addCommand('onStepperValueChanged')
