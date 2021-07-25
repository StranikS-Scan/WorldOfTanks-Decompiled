# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/buy_dormitory_dialog_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class BuyDormitoryDialogModel(FullScreenDialogWindowModel):
    __slots__ = ()
    PRICE_TOOLTIP = 'priceTooltip'

    def __init__(self, properties=15, commands=3):
        super(BuyDormitoryDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(11)

    def getNewDormRooms(self):
        return self._getNumber(12)

    def setNewDormRooms(self, value):
        self._setNumber(12, value)

    def getWarningText(self):
        return self._getResource(13)

    def setWarningText(self, value):
        self._setResource(13, value)

    def getIsBuyingEnabled(self):
        return self._getBool(14)

    def setIsBuyingEnabled(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(BuyDormitoryDialogModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addNumberProperty('newDormRooms', 0)
        self._addResourceProperty('warningText', R.invalid())
        self._addBoolProperty('isBuyingEnabled', False)
