# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/progression_crew_books_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.progression_crew_book_model import ProgressionCrewBookModel

class ProgressionCrewBooksModel(ViewModel):
    __slots__ = ('onApplyClick', 'onCrewBookBuy', 'onCrewBookClick')

    def __init__(self, properties=6, commands=3):
        super(ProgressionCrewBooksModel, self).__init__(properties=properties, commands=commands)

    def getCurrentNation(self):
        return self._getString(0)

    def setCurrentNation(self, value):
        self._setString(0, value)

    def getAvailableNations(self):
        return self._getString(1)

    def setAvailableNations(self, value):
        self._setString(1, value)

    def getIsInvalidDetachment(self):
        return self._getBool(2)

    def setIsInvalidDetachment(self, value):
        self._setBool(2, value)

    def getIsMaxLevelDetachment(self):
        return self._getBool(3)

    def setIsMaxLevelDetachment(self, value):
        self._setBool(3, value)

    def getIsBooksAvailable(self):
        return self._getBool(4)

    def setIsBooksAvailable(self, value):
        self._setBool(4, value)

    def getCrewBooksList(self):
        return self._getArray(5)

    def setCrewBooksList(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(ProgressionCrewBooksModel, self)._initialize()
        self._addStringProperty('currentNation', '')
        self._addStringProperty('availableNations', '')
        self._addBoolProperty('isInvalidDetachment', False)
        self._addBoolProperty('isMaxLevelDetachment', False)
        self._addBoolProperty('isBooksAvailable', False)
        self._addArrayProperty('crewBooksList', Array())
        self.onApplyClick = self._addCommand('onApplyClick')
        self.onCrewBookBuy = self._addCommand('onCrewBookBuy')
        self.onCrewBookClick = self._addCommand('onCrewBookClick')
