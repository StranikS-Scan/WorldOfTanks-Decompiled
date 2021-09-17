# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/marathon_entry_point_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.marathon.base_event_model import BaseEventModel

class MarathonEntryPointModel(ViewModel):
    __slots__ = ('onClick',)
    STATE_MARATHON_DISABLED = -1
    STATE_MARATHON_NOT_STARTED = 0
    STATE_MARATHON_IN_PROGRESS = 1
    STATE_MARATHON_FINISHED = 3

    def __init__(self, properties=14, commands=1):
        super(MarathonEntryPointModel, self).__init__(properties=properties, commands=commands)

    @property
    def progressGrind(self):
        return self._getViewModel(0)

    @property
    def progressPro(self):
        return self._getViewModel(1)

    @property
    def progressPost(self):
        return self._getViewModel(2)

    def getState(self):
        return self._getNumber(3)

    def setState(self, value):
        self._setNumber(3, value)

    def getTimeTillNextState(self):
        return self._getNumber(4)

    def setTimeTillNextState(self, value):
        self._setNumber(4, value)

    def getFormattedTimeTillNextState(self):
        return self._getString(5)

    def setFormattedTimeTillNextState(self, value):
        self._setString(5, value)

    def getCurrentPhase(self):
        return self._getNumber(6)

    def setCurrentPhase(self, value):
        self._setNumber(6, value)

    def getRewardObtained(self):
        return self._getBool(7)

    def setRewardObtained(self, value):
        self._setBool(7, value)

    def getIsPremShopURL(self):
        return self._getBool(8)

    def setIsPremShopURL(self, value):
        self._setBool(8, value)

    def getIsPostProgression(self):
        return self._getBool(9)

    def setIsPostProgression(self, value):
        self._setBool(9, value)

    def getDiscount(self):
        return self._getNumber(10)

    def setDiscount(self, value):
        self._setNumber(10, value)

    def getTokenTemplate(self):
        return self._getString(11)

    def setTokenTemplate(self, value):
        self._setString(11, value)

    def getTokenDoneTemplate(self):
        return self._getString(12)

    def setTokenDoneTemplate(self, value):
        self._setString(12, value)

    def getUserTokens(self):
        return self._getArray(13)

    def setUserTokens(self, value):
        self._setArray(13, value)

    def _initialize(self):
        super(MarathonEntryPointModel, self)._initialize()
        self._addViewModelProperty('progressGrind', UserListModel())
        self._addViewModelProperty('progressPro', UserListModel())
        self._addViewModelProperty('progressPost', UserListModel())
        self._addNumberProperty('state', -1)
        self._addNumberProperty('timeTillNextState', -1)
        self._addStringProperty('formattedTimeTillNextState', '')
        self._addNumberProperty('currentPhase', -1)
        self._addBoolProperty('rewardObtained', False)
        self._addBoolProperty('isPremShopURL', False)
        self._addBoolProperty('isPostProgression', False)
        self._addNumberProperty('discount', 0)
        self._addStringProperty('tokenTemplate', '')
        self._addStringProperty('tokenDoneTemplate', '')
        self._addArrayProperty('userTokens', Array())
        self.onClick = self._addCommand('onClick')
