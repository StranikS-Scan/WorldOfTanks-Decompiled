# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_main_widget_model.py
from new_year.gui.impl.gen.view_models.common.ny_event_state_model import NyEventStateModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearMainWidgetModel(NyWithRomanNumbersModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=16, commands=1):
        super(NewYearMainWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventState(self):
        return self._getViewModel(1)

    @staticmethod
    def getEventStateType():
        return NyEventStateModel

    def getBonusValue(self):
        return self._getReal(2)

    def setBonusValue(self, value):
        self._setReal(2, value)

    def getAnimationType(self):
        return self._getString(3)

    def setAnimationType(self, value):
        self._setString(3, value)

    def getLobbyMode(self):
        return self._getBool(4)

    def setLobbyMode(self, value):
        self._setBool(4, value)

    def getUserLanguage(self):
        return self._getString(5)

    def setUserLanguage(self, value):
        self._setString(5, value)

    def getLevel(self):
        return self._getNumber(6)

    def setLevel(self, value):
        self._setNumber(6, value)

    def getLevelRoman(self):
        return self._getString(7)

    def setLevelRoman(self, value):
        self._setString(7, value)

    def getCurrentPoints(self):
        return self._getNumber(8)

    def setCurrentPoints(self, value):
        self._setNumber(8, value)

    def getNextPoints(self):
        return self._getNumber(9)

    def setNextPoints(self, value):
        self._setNumber(9, value)

    def getIsExtendedAnim(self):
        return self._getBool(10)

    def setIsExtendedAnim(self, value):
        self._setBool(10, value)

    def getIsVisible(self):
        return self._getBool(11)

    def setIsVisible(self, value):
        self._setBool(11, value)

    def getIsEnabled(self):
        return self._getBool(12)

    def setIsEnabled(self, value):
        self._setBool(12, value)

    def getIsInited(self):
        return self._getBool(13)

    def setIsInited(self, value):
        self._setBool(13, value)

    def getIsFirstEntrance(self):
        return self._getBool(14)

    def setIsFirstEntrance(self, value):
        self._setBool(14, value)

    def getIsActiveWidgetTransitionShown(self):
        return self._getBool(15)

    def setIsActiveWidgetTransitionShown(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(NewYearMainWidgetModel, self)._initialize()
        self._addViewModelProperty('eventState', NyEventStateModel())
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
        self._addBoolProperty('isFirstEntrance', True)
        self._addBoolProperty('isActiveWidgetTransitionShown', False)
        self.onClick = self._addCommand('onClick')
