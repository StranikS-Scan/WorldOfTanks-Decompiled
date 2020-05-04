# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/mission_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.reward_model import RewardModel

class MissionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(MissionModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardList(self):
        return self._getViewModel(0)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getIsAvailable(self):
        return self._getBool(2)

    def setIsAvailable(self, value):
        self._setBool(2, value)

    def getStage(self):
        return self._getNumber(3)

    def setStage(self, value):
        self._setNumber(3, value)

    def getProgress(self):
        return self._getNumber(4)

    def setProgress(self, value):
        self._setNumber(4, value)

    def getMaxProgress(self):
        return self._getNumber(5)

    def setMaxProgress(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(MissionModel, self)._initialize()
        self._addViewModelProperty('rewardList', UserListModel())
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isAvailable', False)
        self._addNumberProperty('stage', 0)
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('maxProgress', 0)
