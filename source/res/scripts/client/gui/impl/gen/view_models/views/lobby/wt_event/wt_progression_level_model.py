# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_progression_level_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_bonus_model import WtBonusModel

class WtProgressionLevelModel(ViewModel):
    __slots__ = ()
    DISABLED = 0
    NOT_REACHED = 1
    REACHED = 2
    NOT_CHOSEN = 3

    def __init__(self, properties=2, commands=0):
        super(WtProgressionLevelModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardItems(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardItemsType():
        return WtBonusModel

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WtProgressionLevelModel, self)._initialize()
        self._addViewModelProperty('rewardItems', UserListModel())
        self._addNumberProperty('level', 0)
