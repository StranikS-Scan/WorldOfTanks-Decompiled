# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_rewards_selection_view_model.py
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_base_model import SelectableRewardBaseModel

class PersonalMissionsRewardsSelectionViewModel(SelectableRewardBaseModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PersonalMissionsRewardsSelectionViewModel, self).__init__(properties=properties, commands=commands)

    def getQuestId(self):
        return self._getNumber(1)

    def setQuestId(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(PersonalMissionsRewardsSelectionViewModel, self)._initialize()
        self._addNumberProperty('questId', 0)
