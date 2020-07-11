# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crystals_promo/battle_type_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.crystals_promo.condition_model import ConditionModel

class BattleTypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattleTypeModel, self).__init__(properties=properties, commands=commands)

    @property
    def conditions(self):
        return self._getViewModel(0)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(BattleTypeModel, self)._initialize()
        self._addViewModelProperty('conditions', UserListModel())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('icon', R.invalid())
