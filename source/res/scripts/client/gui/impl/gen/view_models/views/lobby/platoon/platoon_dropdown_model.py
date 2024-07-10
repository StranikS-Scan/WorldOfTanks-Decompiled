# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/platoon_dropdown_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.button_model import ButtonModel

class Type(Enum):
    RANDOM = 'random'
    COMP7 = 'comp7'


class PlatoonDropdownModel(ViewModel):
    __slots__ = ('onOutsideClick',)

    def __init__(self, properties=11, commands=1):
        super(PlatoonDropdownModel, self).__init__(properties=properties, commands=commands)

    @property
    def findPlatoon(self):
        return self._getViewModel(0)

    @staticmethod
    def getFindPlatoonType():
        return ButtonModel

    @property
    def createPlatoon(self):
        return self._getViewModel(1)

    @staticmethod
    def getCreatePlatoonType():
        return ButtonModel

    @property
    def createPlatoonForTwo(self):
        return self._getViewModel(2)

    @staticmethod
    def getCreatePlatoonForTwoType():
        return ButtonModel

    @property
    def createPlatoonForSeven(self):
        return self._getViewModel(3)

    @staticmethod
    def getCreatePlatoonForSevenType():
        return ButtonModel

    def getType(self):
        return Type(self._getString(4))

    def setType(self, value):
        self._setString(4, value.value)

    def getBattleType(self):
        return self._getString(5)

    def setBattleType(self, value):
        self._setString(5, value)

    def getIsSettingsVisible(self):
        return self._getBool(6)

    def setIsSettingsVisible(self, value):
        self._setBool(6, value)

    def getHasXpBonus(self):
        return self._getBool(7)

    def setHasXpBonus(self, value):
        self._setBool(7, value)

    def getHasCreditsBonus(self):
        return self._getBool(8)

    def setHasCreditsBonus(self, value):
        self._setBool(8, value)

    def getIsRibbonVisible(self):
        return self._getBool(9)

    def setIsRibbonVisible(self, value):
        self._setBool(9, value)

    def getBackgroundImage(self):
        return self._getString(10)

    def setBackgroundImage(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(PlatoonDropdownModel, self)._initialize()
        self._addViewModelProperty('findPlatoon', ButtonModel())
        self._addViewModelProperty('createPlatoon', ButtonModel())
        self._addViewModelProperty('createPlatoonForTwo', ButtonModel())
        self._addViewModelProperty('createPlatoonForSeven', ButtonModel())
        self._addStringProperty('type')
        self._addStringProperty('battleType', '')
        self._addBoolProperty('isSettingsVisible', False)
        self._addBoolProperty('hasXpBonus', False)
        self._addBoolProperty('hasCreditsBonus', False)
        self._addBoolProperty('isRibbonVisible', False)
        self._addStringProperty('backgroundImage', '')
        self.onOutsideClick = self._addCommand('onOutsideClick')
