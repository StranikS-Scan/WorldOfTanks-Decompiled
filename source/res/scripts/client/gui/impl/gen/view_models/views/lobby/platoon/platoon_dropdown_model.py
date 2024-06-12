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

    def __init__(self, properties=8, commands=1):
        super(PlatoonDropdownModel, self).__init__(properties=properties, commands=commands)

    @property
    def btnFind(self):
        return self._getViewModel(0)

    @staticmethod
    def getBtnFindType():
        return ButtonModel

    @property
    def btnCreate(self):
        return self._getViewModel(1)

    @staticmethod
    def getBtnCreateType():
        return ButtonModel

    @property
    def btnCreateForTwo(self):
        return self._getViewModel(2)

    @staticmethod
    def getBtnCreateForTwoType():
        return ButtonModel

    def getType(self):
        return Type(self._getString(3))

    def setType(self, value):
        self._setString(3, value.value)

    def getBattleType(self):
        return self._getString(4)

    def setBattleType(self, value):
        self._setString(4, value)

    def getIsSettingsVisible(self):
        return self._getBool(5)

    def setIsSettingsVisible(self, value):
        self._setBool(5, value)

    def getIsRibbonVisible(self):
        return self._getBool(6)

    def setIsRibbonVisible(self, value):
        self._setBool(6, value)

    def getBackgroundImage(self):
        return self._getString(7)

    def setBackgroundImage(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(PlatoonDropdownModel, self)._initialize()
        self._addViewModelProperty('btnFind', ButtonModel())
        self._addViewModelProperty('btnCreate', ButtonModel())
        self._addViewModelProperty('btnCreateForTwo', ButtonModel())
        self._addStringProperty('type')
        self._addStringProperty('battleType', '')
        self._addBoolProperty('isSettingsVisible', False)
        self._addBoolProperty('isRibbonVisible', False)
        self._addStringProperty('backgroundImage', '')
        self.onOutsideClick = self._addCommand('onOutsideClick')
