# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_progress_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.reward_model import RewardModel

class ActionProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ActionProgressModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardList(self):
        return self._getViewModel(0)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getProgress(self):
        return self._getNumber(2)

    def setProgress(self, value):
        self._setNumber(2, value)

    def getProgressMax(self):
        return self._getNumber(3)

    def setProgressMax(self, value):
        self._setNumber(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ActionProgressModel, self)._initialize()
        self._addViewModelProperty('rewardList', UserListModel())
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('progressMax', 0)
        self._addNumberProperty('level', 0)
