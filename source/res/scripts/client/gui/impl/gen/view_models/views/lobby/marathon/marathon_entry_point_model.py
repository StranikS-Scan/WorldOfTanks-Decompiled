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

    def __init__(self, properties=16, commands=1):
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

    def getTimeTillNextQuest(self):
        return self._getNumber(6)

    def setTimeTillNextQuest(self, value):
        self._setNumber(6, value)

    def getFormattedTimeTillNextQuest(self):
        return self._getString(7)

    def setFormattedTimeTillNextQuest(self, value):
        self._setString(7, value)

    def getCurrentPhase(self):
        return self._getNumber(8)

    def setCurrentPhase(self, value):
        self._setNumber(8, value)

    def getRewardObtained(self):
        return self._getBool(9)

    def setRewardObtained(self, value):
        self._setBool(9, value)

    def getIsPremShopURL(self):
        return self._getBool(10)

    def setIsPremShopURL(self, value):
        self._setBool(10, value)

    def getIsPostProgression(self):
        return self._getBool(11)

    def setIsPostProgression(self, value):
        self._setBool(11, value)

    def getDiscount(self):
        return self._getReal(12)

    def setDiscount(self, value):
        self._setReal(12, value)

    def getTokenTemplate(self):
        return self._getString(13)

    def setTokenTemplate(self, value):
        self._setString(13, value)

    def getTokenDoneTemplate(self):
        return self._getString(14)

    def setTokenDoneTemplate(self, value):
        self._setString(14, value)

    def getUserTokens(self):
        return self._getArray(15)

    def setUserTokens(self, value):
        self._setArray(15, value)

    def _initialize(self):
        super(MarathonEntryPointModel, self)._initialize()
        self._addViewModelProperty('progressGrind', UserListModel())
        self._addViewModelProperty('progressPro', UserListModel())
        self._addViewModelProperty('progressPost', UserListModel())
        self._addNumberProperty('state', -1)
        self._addNumberProperty('timeTillNextState', -1)
        self._addStringProperty('formattedTimeTillNextState', '')
        self._addNumberProperty('timeTillNextQuest', -1)
        self._addStringProperty('formattedTimeTillNextQuest', '')
        self._addNumberProperty('currentPhase', -1)
        self._addBoolProperty('rewardObtained', False)
        self._addBoolProperty('isPremShopURL', False)
        self._addBoolProperty('isPostProgression', False)
        self._addRealProperty('discount', 0.0)
        self._addStringProperty('tokenTemplate', '')
        self._addStringProperty('tokenDoneTemplate', '')
        self._addArrayProperty('userTokens', Array())
        self.onClick = self._addCommand('onClick')
