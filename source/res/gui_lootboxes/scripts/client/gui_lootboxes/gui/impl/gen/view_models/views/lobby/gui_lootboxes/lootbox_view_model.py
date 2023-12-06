# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootbox_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.guaranteed_reward_model import GuaranteedRewardModel

class LootboxViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(LootboxViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getGuaranteedRewardType():
        return GuaranteedRewardModel

    def getBoxID(self):
        return self._getNumber(1)

    def setBoxID(self, value):
        self._setNumber(1, value)

    def getBoxType(self):
        return self._getString(2)

    def setBoxType(self, value):
        self._setString(2, value)

    def getCategory(self):
        return self._getString(3)

    def setCategory(self, value):
        self._setString(3, value)

    def getCount(self):
        return self._getNumber(4)

    def setCount(self, value):
        self._setNumber(4, value)

    def getTier(self):
        return self._getNumber(5)

    def setTier(self, value):
        self._setNumber(5, value)

    def getIsOpenEnabled(self):
        return self._getBool(6)

    def setIsOpenEnabled(self, value):
        self._setBool(6, value)

    def getAutoOpenTime(self):
        return self._getNumber(7)

    def setAutoOpenTime(self, value):
        self._setNumber(7, value)

    def getIconName(self):
        return self._getString(8)

    def setIconName(self, value):
        self._setString(8, value)

    def getUserName(self):
        return self._getString(9)

    def setUserName(self, value):
        self._setString(9, value)

    def getDescriptionKey(self):
        return self._getString(10)

    def setDescriptionKey(self, value):
        self._setString(10, value)

    def getVideoRes(self):
        return self._getResource(11)

    def setVideoRes(self, value):
        self._setResource(11, value)

    def getBonusGroups(self):
        return self._getArray(12)

    def setBonusGroups(self, value):
        self._setArray(12, value)

    @staticmethod
    def getBonusGroupsType():
        return unicode

    def getProgressionStage(self):
        return self._getNumber(13)

    def setProgressionStage(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(LootboxViewModel, self)._initialize()
        self._addViewModelProperty('guaranteedReward', GuaranteedRewardModel())
        self._addNumberProperty('boxID', 0)
        self._addStringProperty('boxType', 'unknown')
        self._addStringProperty('category', '')
        self._addNumberProperty('count', 0)
        self._addNumberProperty('tier', 0)
        self._addBoolProperty('isOpenEnabled', True)
        self._addNumberProperty('autoOpenTime', 0)
        self._addStringProperty('iconName', 'unknown')
        self._addStringProperty('userName', 'unknown')
        self._addStringProperty('descriptionKey', 'unknown')
        self._addResourceProperty('videoRes', R.invalid())
        self._addArrayProperty('bonusGroups', Array())
        self._addNumberProperty('progressionStage', 0)
