# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/confirmation_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel

class ConfirmationModel(ViewModel):
    __slots__ = ('confirm', 'cancel')

    def __init__(self, properties=2, commands=2):
        super(ConfirmationModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceItemModel

    def getEventName(self):
        return self._getString(1)

    def setEventName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ConfirmationModel, self)._initialize()
        self._addViewModelProperty('price', PriceItemModel())
        self._addStringProperty('eventName', '')
        self.confirm = self._addCommand('confirm')
        self.cancel = self._addCommand('cancel')
