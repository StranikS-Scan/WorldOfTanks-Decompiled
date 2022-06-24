# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_quests_chain_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.key_value_model import KeyValueModel

class BattlePassQuestsChainTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattlePassQuestsChainTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return KeyValueModel

    def _initialize(self):
        super(BattlePassQuestsChainTooltipViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
