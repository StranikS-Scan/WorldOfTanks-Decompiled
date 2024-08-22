# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/nps_intro_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel

class CloseReason(Enum):
    ESC = 'esc'
    CLOSE = 'close'
    VIEWCHANGES = 'view_changes'
    SKIPCHANGES = 'skip_changes'


class NpsIntroViewModel(ViewModel):
    __slots__ = ('onViewChanges', 'onSkipChanges', 'onClose')

    def __init__(self, properties=2, commands=3):
        super(NpsIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getAdditionalRewards(self):
        return self._getArray(1)

    def setAdditionalRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getAdditionalRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(NpsIntroViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self.onViewChanges = self._addCommand('onViewChanges')
        self.onSkipChanges = self._addCommand('onSkipChanges')
        self.onClose = self._addCommand('onClose')
