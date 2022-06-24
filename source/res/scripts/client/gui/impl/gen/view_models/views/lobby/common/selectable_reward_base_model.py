# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/selectable_reward_base_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_model import SelectableRewardModel

class SelectableRewardBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SelectableRewardBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectableRewardModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getSelectableRewardModelType():
        return SelectableRewardModel

    def _initialize(self):
        super(SelectableRewardBaseModel, self)._initialize()
        self._addViewModelProperty('selectableRewardModel', SelectableRewardModel())
