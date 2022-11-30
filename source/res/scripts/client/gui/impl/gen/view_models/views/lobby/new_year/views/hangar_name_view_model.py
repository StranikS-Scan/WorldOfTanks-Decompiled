# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/hangar_name_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_hangar_name_model import NyHangarNameModel

class Action(Enum):
    SELECT = 'select'
    CHANGE = 'change'


class HangarNameViewModel(ViewModel):
    __slots__ = ('onSubmitName', 'onChangeAll', 'onChangeTitle', 'onChangeDescription', 'onAnimationRelease', 'enableBlur')

    def __init__(self, properties=3, commands=6):
        super(HangarNameViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def hangarName(self):
        return self._getViewModel(0)

    @staticmethod
    def getHangarNameType():
        return NyHangarNameModel

    def getAction(self):
        return Action(self._getString(1))

    def setAction(self, value):
        self._setString(1, value.value)

    def getShowError(self):
        return self._getBool(2)

    def setShowError(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(HangarNameViewModel, self)._initialize()
        self._addViewModelProperty('hangarName', NyHangarNameModel())
        self._addStringProperty('action')
        self._addBoolProperty('showError', False)
        self.onSubmitName = self._addCommand('onSubmitName')
        self.onChangeAll = self._addCommand('onChangeAll')
        self.onChangeTitle = self._addCommand('onChangeTitle')
        self.onChangeDescription = self._addCommand('onChangeDescription')
        self.onAnimationRelease = self._addCommand('onAnimationRelease')
        self.enableBlur = self._addCommand('enableBlur')
