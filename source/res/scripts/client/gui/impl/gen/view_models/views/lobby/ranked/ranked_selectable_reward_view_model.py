# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_selectable_reward_view_model.py
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_base_model import SelectableRewardBaseModel

class RankedSelectableRewardViewModel(SelectableRewardBaseModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RankedSelectableRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getRewardType(self):
        return self._getString(1)

    def setRewardType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(RankedSelectableRewardViewModel, self)._initialize()
        self._addStringProperty('rewardType', '')
