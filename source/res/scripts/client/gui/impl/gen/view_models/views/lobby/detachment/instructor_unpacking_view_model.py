# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructor_unpacking_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.rose_model import RoseModel
from gui.impl.gen.view_models.views.lobby.detachment.instructor_unpacking.unpacking_info_model import UnpackingInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.instructor_unpacking.unpacking_perks_info_model import UnpackingPerksInfoModel

class InstructorUnpackingViewModel(NavigationViewModel):
    __slots__ = ('onNationClick', 'onTabClick', 'onNextClick', 'onPreviousClick', 'onLearnClick', 'onVoiceListenClick', 'onPerkClick')

    def __init__(self, properties=11, commands=10):
        super(InstructorUnpackingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentInfo(self):
        return self._getViewModel(2)

    @property
    def roseModel(self):
        return self._getViewModel(3)

    @property
    def information(self):
        return self._getViewModel(4)

    @property
    def perksInfo(self):
        return self._getViewModel(5)

    def getId(self):
        return self._getNumber(6)

    def setId(self, value):
        self._setNumber(6, value)

    def getBackground(self):
        return self._getResource(7)

    def setBackground(self, value):
        self._setResource(7, value)

    def getIcon(self):
        return self._getString(8)

    def setIcon(self, value):
        self._setString(8, value)

    def getSelectedNation(self):
        return self._getString(9)

    def setSelectedNation(self, value):
        self._setString(9, value)

    def getNations(self):
        return self._getArray(10)

    def setNations(self, value):
        self._setArray(10, value)

    def _initialize(self):
        super(InstructorUnpackingViewModel, self)._initialize()
        self._addViewModelProperty('detachmentInfo', DetachmentShortInfoModel())
        self._addViewModelProperty('roseModel', RoseModel())
        self._addViewModelProperty('information', UnpackingInfoModel())
        self._addViewModelProperty('perksInfo', UnpackingPerksInfoModel())
        self._addNumberProperty('id', 0)
        self._addResourceProperty('background', R.invalid())
        self._addStringProperty('icon', '')
        self._addStringProperty('selectedNation', '')
        self._addArrayProperty('nations', Array())
        self.onNationClick = self._addCommand('onNationClick')
        self.onTabClick = self._addCommand('onTabClick')
        self.onNextClick = self._addCommand('onNextClick')
        self.onPreviousClick = self._addCommand('onPreviousClick')
        self.onLearnClick = self._addCommand('onLearnClick')
        self.onVoiceListenClick = self._addCommand('onVoiceListenClick')
        self.onPerkClick = self._addCommand('onPerkClick')
