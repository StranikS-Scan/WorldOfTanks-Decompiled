# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/preview_view_model.py
from enum import Enum
from halloween.gui.impl.gen.view_models.views.lobby.common.base_view_model import BaseViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.crew_list_model import CrewListModel

class PreviewTypeEnum(Enum):
    INTRO = 'intro'
    HISTORY = 'history'
    WITCHES = 'witches'
    OUTRO = 'outro'


class PreviewViewModel(BaseViewModel):
    __slots__ = ('onBack', 'onSoundBtnClick', 'onSlideClick')

    def __init__(self, properties=9, commands=4):
        super(PreviewViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def crewListBlock(self):
        return self._getViewModel(2)

    @staticmethod
    def getCrewListBlockType():
        return CrewListModel

    def getType(self):
        return PreviewTypeEnum(self._getString(3))

    def setType(self, value):
        self._setString(3, value.value)

    def getDisabledIntro(self):
        return self._getBool(4)

    def setDisabledIntro(self, value):
        self._setBool(4, value)

    def getDisabledOutro(self):
        return self._getBool(5)

    def setDisabledOutro(self, value):
        self._setBool(5, value)

    def getNewIntro(self):
        return self._getBool(6)

    def setNewIntro(self, value):
        self._setBool(6, value)

    def getNewOutro(self):
        return self._getBool(7)

    def setNewOutro(self, value):
        self._setBool(7, value)

    def getIsPerformanceRiskLow(self):
        return self._getBool(8)

    def setIsPerformanceRiskLow(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(PreviewViewModel, self)._initialize()
        self._addViewModelProperty('crewListBlock', CrewListModel())
        self._addStringProperty('type')
        self._addBoolProperty('disabledIntro', False)
        self._addBoolProperty('disabledOutro', False)
        self._addBoolProperty('newIntro', False)
        self._addBoolProperty('newOutro', False)
        self._addBoolProperty('isPerformanceRiskLow', False)
        self.onBack = self._addCommand('onBack')
        self.onSoundBtnClick = self._addCommand('onSoundBtnClick')
        self.onSlideClick = self._addCommand('onSlideClick')
