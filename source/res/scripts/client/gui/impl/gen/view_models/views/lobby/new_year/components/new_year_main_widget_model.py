# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_main_widget_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearMainWidgetModel(NyWithRomanNumbersModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=9, commands=1):
        super(NewYearMainWidgetModel, self).__init__(properties=properties, commands=commands)

    def getAnimationType(self):
        return self._getString(1)

    def setAnimationType(self, value):
        self._setString(1, value)

    def getLobbyMode(self):
        return self._getBool(2)

    def setLobbyMode(self, value):
        self._setBool(2, value)

    def getUserLanguage(self):
        return self._getString(3)

    def setUserLanguage(self, value):
        self._setString(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getLevelRoman(self):
        return self._getString(5)

    def setLevelRoman(self, value):
        self._setString(5, value)

    def getCurrentPoints(self):
        return self._getNumber(6)

    def setCurrentPoints(self, value):
        self._setNumber(6, value)

    def getNextPoints(self):
        return self._getNumber(7)

    def setNextPoints(self, value):
        self._setNumber(7, value)

    def getIsExtendedAnim(self):
        return self._getBool(8)

    def setIsExtendedAnim(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(NewYearMainWidgetModel, self)._initialize()
        self._addStringProperty('animationType', 'none')
        self._addBoolProperty('lobbyMode', True)
        self._addStringProperty('userLanguage', '')
        self._addNumberProperty('level', 1)
        self._addStringProperty('levelRoman', '')
        self._addNumberProperty('currentPoints', 1)
        self._addNumberProperty('nextPoints', 1)
        self._addBoolProperty('isExtendedAnim', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
