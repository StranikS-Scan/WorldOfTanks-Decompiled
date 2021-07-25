# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/new_level_window_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.reward_model import RewardModel

class NewLevelWindowModel(NavigationViewModel):
    __slots__ = ('onGoToBadges', 'onGoToPersonalCase')

    def __init__(self, properties=5, commands=5):
        super(NewLevelWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachmentInfo(self):
        return self._getViewModel(2)

    def getRewardsList(self):
        return self._getArray(3)

    def setRewardsList(self, value):
        self._setArray(3, value)

    def getEliteTitle(self):
        return self._getResource(4)

    def setEliteTitle(self, value):
        self._setResource(4, value)

    def _initialize(self):
        super(NewLevelWindowModel, self)._initialize()
        self._addViewModelProperty('detachmentInfo', DetachmentShortInfoModel())
        self._addArrayProperty('rewardsList', Array())
        self._addResourceProperty('eliteTitle', R.invalid())
        self.onGoToBadges = self._addCommand('onGoToBadges')
        self.onGoToPersonalCase = self._addCommand('onGoToPersonalCase')
