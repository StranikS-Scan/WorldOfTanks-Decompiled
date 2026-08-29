# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portals/wt_portal_view_model.py
from frameworks.wulf import Array
from white_tiger.gui.impl.gen.view_models.views.lobby.common.wt_guaranteed_reward_model import WtGuaranteedRewardModel
from white_tiger.gui.impl.gen.view_models.views.lobby.common.wt_run_portal_model import WtRunPortalModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_base_portals_view_model import WtBasePortalsViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_bonus_model import WtPortalBonusModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_rewardList import WtPortalRewardlist

class WtPortalViewModel(WtBasePortalsViewModel):
    __slots__ = ('onGoBack', 'onRunPortal', 'onSwitchAnimation', 'onPreview')

    def __init__(self, properties=16, commands=6):
        super(WtPortalViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalRun(self):
        return self._getViewModel(1)

    @staticmethod
    def getPortalRunType():
        return WtRunPortalModel

    @property
    def guaranteedReward(self):
        return self._getViewModel(2)

    @staticmethod
    def getGuaranteedRewardType():
        return WtGuaranteedRewardModel

    def getPortalType(self):
        return self._getString(3)

    def setPortalType(self, value):
        self._setString(3, value)

    def getSelectedLootBoxesCount(self):
        return self._getNumber(4)

    def setSelectedLootBoxesCount(self, value):
        self._setNumber(4, value)

    def getBackButtonText(self):
        return self._getString(5)

    def setBackButtonText(self, value):
        self._setString(5, value)

    def getFirstLaunchReward(self):
        return self._getNumber(6)

    def setFirstLaunchReward(self, value):
        self._setNumber(6, value)

    def getIsLaunchAnimated(self):
        return self._getBool(7)

    def setIsLaunchAnimated(self, value):
        self._setBool(7, value)

    def getHighProbability(self):
        return self._getReal(8)

    def setHighProbability(self, value):
        self._setReal(8, value)

    def getMediumProbability(self):
        return self._getReal(9)

    def setMediumProbability(self, value):
        self._setReal(9, value)

    def getLowProbability(self):
        return self._getReal(10)

    def setLowProbability(self, value):
        self._setReal(10, value)

    def getIsViewActive(self):
        return self._getBool(11)

    def setIsViewActive(self, value):
        self._setBool(11, value)

    def getHighProbabilityRewards(self):
        return self._getArray(12)

    def setHighProbabilityRewards(self, value):
        self._setArray(12, value)

    @staticmethod
    def getHighProbabilityRewardsType():
        return WtPortalBonusModel

    def getMediumProbabilityRewards(self):
        return self._getArray(13)

    def setMediumProbabilityRewards(self, value):
        self._setArray(13, value)

    @staticmethod
    def getMediumProbabilityRewardsType():
        return WtPortalBonusModel

    def getLowProbabilityRewards(self):
        return self._getArray(14)

    def setLowProbabilityRewards(self, value):
        self._setArray(14, value)

    @staticmethod
    def getLowProbabilityRewardsType():
        return WtPortalBonusModel

    def getRewardList(self):
        return self._getArray(15)

    def setRewardList(self, value):
        self._setArray(15, value)

    @staticmethod
    def getRewardListType():
        return WtPortalRewardlist

    def _initialize(self):
        super(WtPortalViewModel, self)._initialize()
        self._addViewModelProperty('portalRun', WtRunPortalModel())
        self._addViewModelProperty('guaranteedReward', WtGuaranteedRewardModel())
        self._addStringProperty('portalType', '')
        self._addNumberProperty('selectedLootBoxesCount', 1)
        self._addStringProperty('backButtonText', '')
        self._addNumberProperty('firstLaunchReward', 100)
        self._addBoolProperty('isLaunchAnimated', False)
        self._addRealProperty('highProbability', 0.0)
        self._addRealProperty('mediumProbability', 0.0)
        self._addRealProperty('lowProbability', 0.0)
        self._addBoolProperty('isViewActive', True)
        self._addArrayProperty('highProbabilityRewards', Array())
        self._addArrayProperty('mediumProbabilityRewards', Array())
        self._addArrayProperty('lowProbabilityRewards', Array())
        self._addArrayProperty('rewardList', Array())
        self.onGoBack = self._addCommand('onGoBack')
        self.onRunPortal = self._addCommand('onRunPortal')
        self.onSwitchAnimation = self._addCommand('onSwitchAnimation')
        self.onPreview = self._addCommand('onPreview')
