# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/awards/multiple_awards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.awards.reward_model import RewardModel

class MultipleAwardsViewModel(ViewModel):
    __slots__ = ('showHangar', 'makeChoice', 'onClose')

    def __init__(self, properties=9, commands=3):
        super(MultipleAwardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getTitleIcon(self):
        return self._getString(2)

    def setTitleIcon(self, value):
        self._setString(2, value)

    def getSubTitle(self):
        return self._getString(3)

    def setSubTitle(self, value):
        self._setString(3, value)

    def getIsRibbonGold(self):
        return self._getBool(4)

    def setIsRibbonGold(self, value):
        self._setBool(4, value)

    def getIsLightVisible(self):
        return self._getBool(5)

    def setIsLightVisible(self, value):
        self._setBool(5, value)

    def getHasVehicleToView(self):
        return self._getBool(6)

    def setHasVehicleToView(self, value):
        self._setBool(6, value)

    def getHasRewardsOnChoice(self):
        return self._getBool(7)

    def setHasRewardsOnChoice(self, value):
        self._setBool(7, value)

    def getMainItemsCount(self):
        return self._getNumber(8)

    def setMainItemsCount(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(MultipleAwardsViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addStringProperty('title', '')
        self._addStringProperty('titleIcon', '')
        self._addStringProperty('subTitle', '')
        self._addBoolProperty('isRibbonGold', False)
        self._addBoolProperty('isLightVisible', False)
        self._addBoolProperty('hasVehicleToView', False)
        self._addBoolProperty('hasRewardsOnChoice', False)
        self._addNumberProperty('mainItemsCount', 0)
        self.showHangar = self._addCommand('showHangar')
        self.makeChoice = self._addCommand('makeChoice')
        self.onClose = self._addCommand('onClose')
