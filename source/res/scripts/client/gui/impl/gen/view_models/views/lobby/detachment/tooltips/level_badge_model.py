# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/level_badge_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.reward_model import RewardModel

class LevelBadgeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(LevelBadgeModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachment(self):
        return self._getViewModel(0)

    def getIsConverted(self):
        return self._getBool(1)

    def setIsConverted(self, value):
        self._setBool(1, value)

    def getTitle(self):
        return self._getResource(2)

    def setTitle(self, value):
        self._setResource(2, value)

    def getNextEliteLevel(self):
        return self._getResource(3)

    def setNextEliteLevel(self, value):
        self._setResource(3, value)

    def getCurrentComponents(self):
        return self._getArray(4)

    def setCurrentComponents(self, value):
        self._setArray(4, value)

    def getNextComponents(self):
        return self._getArray(5)

    def setNextComponents(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(LevelBadgeModel, self)._initialize()
        self._addViewModelProperty('detachment', DetachmentShortInfoModel())
        self._addBoolProperty('isConverted', False)
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('nextEliteLevel', R.invalid())
        self._addArrayProperty('currentComponents', Array())
        self._addArrayProperty('nextComponents', Array())
