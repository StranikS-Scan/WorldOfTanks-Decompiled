# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_undefined_tankman_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.tankman_option_model import TankmanOptionModel

class BattlePassUndefinedTankmanViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattlePassUndefinedTankmanViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def options(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(BattlePassUndefinedTankmanViewModel, self)._initialize()
        self._addViewModelProperty('options', UserListModel())
