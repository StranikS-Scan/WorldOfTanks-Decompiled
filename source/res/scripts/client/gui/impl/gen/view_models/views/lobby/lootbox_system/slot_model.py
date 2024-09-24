# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.bonus_model import BonusModel

class SlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getProbability(self):
        return self._getReal(1)

    def setProbability(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addViewModelProperty('bonuses', UserListModel())
        self._addRealProperty('probability', 0.0)
