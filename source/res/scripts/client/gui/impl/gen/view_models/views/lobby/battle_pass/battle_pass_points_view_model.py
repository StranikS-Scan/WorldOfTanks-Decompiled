# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_points_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class BattlePassPointsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattlePassPointsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def pointsTops(self):
        return self._getViewModel(0)

    @property
    def vehiclesList(self):
        return self._getViewModel(1)

    def _initialize(self):
        super(BattlePassPointsViewModel, self)._initialize()
        self._addViewModelProperty('pointsTops', UserListModel())
        self._addViewModelProperty('vehiclesList', UserListModel())
