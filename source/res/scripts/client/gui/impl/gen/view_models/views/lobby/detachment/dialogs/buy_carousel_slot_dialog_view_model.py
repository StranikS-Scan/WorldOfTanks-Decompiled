# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/buy_carousel_slot_dialog_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class BuyCarouselSlotDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=3):
        super(BuyCarouselSlotDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(11)

    def getHasEmptySlots(self):
        return self._getBool(12)

    def setHasEmptySlots(self, value):
        self._setBool(12, value)

    def getNumberDormitoryRoom(self):
        return self._getNumber(13)

    def setNumberDormitoryRoom(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(BuyCarouselSlotDialogViewModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addBoolProperty('hasEmptySlots', False)
        self._addNumberProperty('numberDormitoryRoom', 0)
