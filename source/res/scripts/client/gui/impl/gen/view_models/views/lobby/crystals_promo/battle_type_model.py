# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crystals_promo/battle_type_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.crystals_promo.condition_model import ConditionModel

class BattleTypeModel(ViewModel):
    __slots__ = ()
    RANDOM = 'random'
    GENERAL = 'general'
    COMP7 = 'comp7'
    RANKED = 'ranked'

    def __init__(self, properties=2, commands=0):
        super(BattleTypeModel, self).__init__(properties=properties, commands=commands)

    @property
    def conditions(self):
        return self._getViewModel(0)

    @staticmethod
    def getConditionsType():
        return ConditionModel

    def getBattleType(self):
        return self._getString(1)

    def setBattleType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(BattleTypeModel, self)._initialize()
        self._addViewModelProperty('conditions', UserListModel())
        self._addStringProperty('battleType', '')
