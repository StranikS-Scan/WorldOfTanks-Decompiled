# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/hangar_name_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_hangar_name_model import NyHangarNameModel

class TypeView(Enum):
    WELCOME = 'welcome'
    CHANGE = 'change'


class HangarNameViewModel(ViewModel):
    __slots__ = ('onSubmitName', 'onKeepName', 'onChangeAll', 'onChangeTitle', 'onChangeDescription', 'onCloseWelcomeScreen', 'onCloseChangeNameScreen')

    def __init__(self, properties=4, commands=7):
        super(HangarNameViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def hangarName(self):
        return self._getViewModel(0)

    @staticmethod
    def getHangarNameType():
        return NyHangarNameModel

    def getTypeView(self):
        return TypeView(self._getString(1))

    def setTypeView(self, value):
        self._setString(1, value.value)

    def getHasChanges(self):
        return self._getBool(2)

    def setHasChanges(self, value):
        self._setBool(2, value)

    def getIsHidden(self):
        return self._getBool(3)

    def setIsHidden(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(HangarNameViewModel, self)._initialize()
        self._addViewModelProperty('hangarName', NyHangarNameModel())
        self._addStringProperty('typeView', TypeView.WELCOME.value)
        self._addBoolProperty('hasChanges', False)
        self._addBoolProperty('isHidden', False)
        self.onSubmitName = self._addCommand('onSubmitName')
        self.onKeepName = self._addCommand('onKeepName')
        self.onChangeAll = self._addCommand('onChangeAll')
        self.onChangeTitle = self._addCommand('onChangeTitle')
        self.onChangeDescription = self._addCommand('onChangeDescription')
        self.onCloseWelcomeScreen = self._addCommand('onCloseWelcomeScreen')
        self.onCloseChangeNameScreen = self._addCommand('onCloseChangeNameScreen')
