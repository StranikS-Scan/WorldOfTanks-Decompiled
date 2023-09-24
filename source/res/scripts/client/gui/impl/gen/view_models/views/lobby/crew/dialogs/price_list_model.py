# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/price_list_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import PriceCardModel

class PriceListModel(ViewModel):
    __slots__ = ('onCardClick',)

    def __init__(self, properties=1, commands=1):
        super(PriceListModel, self).__init__(properties=properties, commands=commands)

    def getCardsList(self):
        return self._getArray(0)

    def setCardsList(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCardsListType():
        return PriceCardModel

    def _initialize(self):
        super(PriceListModel, self)._initialize()
        self._addArrayProperty('cardsList', Array())
        self.onCardClick = self._addCommand('onCardClick')
