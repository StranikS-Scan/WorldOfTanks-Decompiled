# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/bob_personal_rewards_view_model.py
from gui.impl.gen.view_models.views.lobby.bob.bob_common_rewards_view_model import BobCommonRewardsViewModel

class BobPersonalRewardsViewModel(BobCommonRewardsViewModel):
    __slots__ = ('onOpenNext',)

    def __init__(self, properties=3, commands=1):
        super(BobPersonalRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getAvailableCount(self):
        return self._getNumber(2)

    def setAvailableCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BobPersonalRewardsViewModel, self)._initialize()
        self._addNumberProperty('availableCount', 0)
        self.onOpenNext = self._addCommand('onOpenNext')
