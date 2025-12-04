# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_main_widget_model.py
from enum import Enum
from frameworks.wulf import Array
from new_year.gui.impl.gen.view_models.common.ny_event_state_model import NyEventStateModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class State(Enum):
    SAD = 'sad'
    NORMAL = 'normal'
    FUN = 'fun'
    PAUSE = 'pause'
    EMPTY = ''


class PetNeed(Enum):
    FOOD = 'food'
    FUN = 'fun'
    ACTIVITY = 'activity'
    NONE = 'none'


class NewYearMainWidgetModel(NyWithRomanNumbersModel):
    __slots__ = ('onClick', 'onPetClick')

    def __init__(self, properties=23, commands=2):
        super(NewYearMainWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventState(self):
        return self._getViewModel(1)

    @staticmethod
    def getEventStateType():
        return NyEventStateModel

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

    def getIsVisible(self):
        return self._getBool(9)

    def setIsVisible(self, value):
        self._setBool(9, value)

    def getIsEnabled(self):
        return self._getBool(10)

    def setIsEnabled(self, value):
        self._setBool(10, value)

    def getIsInited(self):
        return self._getBool(11)

    def setIsInited(self, value):
        self._setBool(11, value)

    def getIsActiveWidgetTransitionShown(self):
        return self._getBool(12)

    def setIsActiveWidgetTransitionShown(self, value):
        self._setBool(12, value)

    def getLevel(self):
        return self._getNumber(13)

    def setLevel(self, value):
        self._setNumber(13, value)

    def getProgress(self):
        return self._getNumber(14)

    def setProgress(self, value):
        self._setNumber(14, value)

    def getIsFirstEntrance(self):
        return self._getBool(15)

    def setIsFirstEntrance(self, value):
        self._setBool(15, value)

    def getIsPetEntrance(self):
        return self._getBool(16)

    def setIsPetEntrance(self, value):
        self._setBool(16, value)

    def getPetState(self):
        return State(self._getString(17))

    def setPetState(self, value):
        self._setString(17, value.value)

    def getProgressState(self):
        return self._getBool(18)

    def setProgressState(self, value):
        self._setBool(18, value)

    def getPetNeed(self):
        return self._getArray(19)

    def setPetNeed(self, value):
        self._setArray(19, value)

    @staticmethod
    def getPetNeedType():
        return unicode

    def getBonusValue(self):
        return self._getNumber(20)

    def setBonusValue(self, value):
        self._setNumber(20, value)

    def getMaxBonusValue(self):
        return self._getNumber(21)

    def setMaxBonusValue(self, value):
        self._setNumber(21, value)

    def getPetLevelNeed(self):
        return self._getNumber(22)

    def setPetLevelNeed(self, value):
        self._setNumber(22, value)

    def _initialize(self):
        super(NewYearMainWidgetModel, self)._initialize()
        self._addViewModelProperty('eventState', NyEventStateModel())
        self._addStringProperty('animationType', 'none')
        self._addBoolProperty('lobbyMode', True)
        self._addStringProperty('userLanguage', '')
        self._addStringProperty('levelRoman', '')
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('nextPoints', 1)
        self._addBoolProperty('isExtendedAnim', False)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isInited', False)
        self._addBoolProperty('isActiveWidgetTransitionShown', False)
        self._addNumberProperty('level', 0)
        self._addNumberProperty('progress', 0)
        self._addBoolProperty('isFirstEntrance', True)
        self._addBoolProperty('isPetEntrance', True)
        self._addStringProperty('petState')
        self._addBoolProperty('progressState', False)
        self._addArrayProperty('petNeed', Array())
        self._addNumberProperty('bonusValue', 0)
        self._addNumberProperty('maxBonusValue', 0)
        self._addNumberProperty('petLevelNeed', 2)
        self.onClick = self._addCommand('onClick')
        self.onPetClick = self._addCommand('onPetClick')
