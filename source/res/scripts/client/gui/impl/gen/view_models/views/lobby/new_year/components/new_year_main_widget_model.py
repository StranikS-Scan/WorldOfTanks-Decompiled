# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_main_widget_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearMainWidgetModel(NyWithRomanNumbersModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=13, commands=1):
        super(NewYearMainWidgetModel, self).__init__(properties=properties, commands=commands)

    def getBonusValue(self):
        return self._getReal(1)

    def setBonusValue(self, value):
        self._setReal(1, value)

    def getAnimationType(self):
        return self._getString(2)

    def setAnimationType(self, value):
        self._setString(2, value)

    def getLobbyMode(self):
        return self._getBool(3)

    def setLobbyMode(self, value):
        self._setBool(3, value)

    def getUserLanguage(self):
        return self._getString(4)

    def setUserLanguage(self, value):
        self._setString(4, value)

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getLevelRoman(self):
        return self._getString(6)

    def setLevelRoman(self, value):
        self._setString(6, value)

    def getCurrentPoints(self):
        return self._getNumber(7)

    def setCurrentPoints(self, value):
        self._setNumber(7, value)

    def getNextPoints(self):
        return self._getNumber(8)

    def setNextPoints(self, value):
        self._setNumber(8, value)

    def getIsExtendedAnim(self):
        return self._getBool(9)

    def setIsExtendedAnim(self, value):
        self._setBool(9, value)

    def getIsVisible(self):
        return self._getBool(10)

    def setIsVisible(self, value):
        self._setBool(10, value)

    def getIsEnabled(self):
        return self._getBool(11)

    def setIsEnabled(self, value):
        self._setBool(11, value)

    def getIsInited(self):
        return self._getBool(12)

    def setIsInited(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NewYearMainWidgetModel, self)._initialize()
        self._addRealProperty('bonusValue', 0.0)
        self._addStringProperty('animationType', 'none')
        self._addBoolProperty('lobbyMode', True)
        self._addStringProperty('userLanguage', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('levelRoman', '')
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('nextPoints', 1)
        self._addBoolProperty('isExtendedAnim', False)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isInited', False)
        self.onClick = self._addCommand('onClick')
