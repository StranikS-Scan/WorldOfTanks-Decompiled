# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/change_tankman_skin_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_data_card_model import PersonalDataCardModel

class ChangeTankmanSkinViewModel(ViewModel):
    __slots__ = ('onCardSelected', 'onNewCardViewed', 'onResetFilters', 'onViewClose')

    def __init__(self, properties=3, commands=4):
        super(ChangeTankmanSkinViewModel, self).__init__(properties=properties, commands=commands)

    def getIsCardsLocked(self):
        return self._getBool(0)

    def setIsCardsLocked(self, value):
        self._setBool(0, value)

    def getNation(self):
        return self._getString(1)

    def setNation(self, value):
        self._setString(1, value)

    def getCardList(self):
        return self._getArray(2)

    def setCardList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getCardListType():
        return PersonalDataCardModel

    def _initialize(self):
        super(ChangeTankmanSkinViewModel, self)._initialize()
        self._addBoolProperty('isCardsLocked', False)
        self._addStringProperty('nation', '')
        self._addArrayProperty('cardList', Array())
        self.onCardSelected = self._addCommand('onCardSelected')
        self.onNewCardViewed = self._addCommand('onNewCardViewed')
        self.onResetFilters = self._addCommand('onResetFilters')
        self.onViewClose = self._addCommand('onViewClose')
