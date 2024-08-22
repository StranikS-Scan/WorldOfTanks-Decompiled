# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/components/book_training_option_model.py
from gui.impl.gen.view_models.views.lobby.crew.components.training_option_model import TrainingOptionModel

class BookTrainingOptionModel(TrainingOptionModel):
    __slots__ = ('onBuy',)

    def __init__(self, properties=12, commands=3):
        super(BookTrainingOptionModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(3)

    def setIntCD(self, value):
        self._setNumber(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def getIcon(self):
        return self._getString(5)

    def setIcon(self, value):
        self._setString(5, value)

    def getTitle(self):
        return self._getString(6)

    def setTitle(self, value):
        self._setString(6, value)

    def getMainText(self):
        return self._getString(7)

    def setMainText(self, value):
        self._setString(7, value)

    def getAdditionalText(self):
        return self._getString(8)

    def setAdditionalText(self, value):
        self._setString(8, value)

    def getBookAddedXp(self):
        return self._getNumber(9)

    def setBookAddedXp(self, value):
        self._setNumber(9, value)

    def getAvailableCount(self):
        return self._getNumber(10)

    def setAvailableCount(self, value):
        self._setNumber(10, value)

    def getSelectedCount(self):
        return self._getNumber(11)

    def setSelectedCount(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(BookTrainingOptionModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('type', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('title', '')
        self._addStringProperty('mainText', '')
        self._addStringProperty('additionalText', '')
        self._addNumberProperty('bookAddedXp', 0)
        self._addNumberProperty('availableCount', 0)
        self._addNumberProperty('selectedCount', 0)
        self.onBuy = self._addCommand('onBuy')
