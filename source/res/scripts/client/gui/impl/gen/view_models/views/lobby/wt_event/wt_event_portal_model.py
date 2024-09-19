# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_portal_model.py
from enum import Enum
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.portal_premium_tanks import PortalPremiumTanks
from gui.impl.gen.view_models.views.lobby.wt_event.portal_reward import PortalReward
from gui.impl.gen.view_models.views.lobby.wt_event.tank_reward import TankReward
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_guaranteed_award import WtEventGuaranteedAward
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_availability import WtEventPortalAvailability
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portals_base import WtEventPortalsBase

class PortalType(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'
    TANK = 'tank'


class LootBoxType(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'


class WtEventPortalModel(WtEventPortalsBase):
    __slots__ = ('onRunPortalClick', 'onAnimationSettingChange', 'onUpdateLootbox')

    def __init__(self, properties=22, commands=5):
        super(WtEventPortalModel, self).__init__(properties=properties, commands=commands)

    @property
    def inactivePortalAvailability(self):
        return self._getViewModel(2)

    @staticmethod
    def getInactivePortalAvailabilityType():
        return WtEventPortalAvailability

    @property
    def portalAvailability(self):
        return self._getViewModel(3)

    @staticmethod
    def getPortalAvailabilityType():
        return WtEventPortalAvailability

    @property
    def bossSpecificRewards(self):
        return self._getViewModel(4)

    @staticmethod
    def getBossSpecificRewardsType():
        return PortalReward

    @property
    def guaranteedRewards(self):
        return self._getViewModel(5)

    @staticmethod
    def getGuaranteedRewardsType():
        return PortalReward

    @property
    def rewards(self):
        return self._getViewModel(6)

    @staticmethod
    def getRewardsType():
        return PortalReward

    @property
    def collectionReward(self):
        return self._getViewModel(7)

    @staticmethod
    def getCollectionRewardType():
        return PortalReward

    @property
    def customizationReward(self):
        return self._getViewModel(8)

    @staticmethod
    def getCustomizationRewardType():
        return PortalReward

    @property
    def rewardTanks(self):
        return self._getViewModel(9)

    @staticmethod
    def getRewardTanksType():
        return TankReward

    @property
    def rentalTank(self):
        return self._getViewModel(10)

    @staticmethod
    def getRentalTankType():
        return PortalReward

    @property
    def tanks(self):
        return self._getViewModel(11)

    @staticmethod
    def getTanksType():
        return PortalPremiumTanks

    @property
    def guaranteedAward(self):
        return self._getViewModel(12)

    @staticmethod
    def getGuaranteedAwardType():
        return WtEventGuaranteedAward

    def getPortalType(self):
        return PortalType(self._getString(13))

    def setPortalType(self, value):
        self._setString(13, value.value)

    def getBackButtonText(self):
        return self._getString(14)

    def setBackButtonText(self, value):
        self._setString(14, value)

    def getDefaultRunPortalTimes(self):
        return self._getNumber(15)

    def setDefaultRunPortalTimes(self, value):
        self._setNumber(15, value)

    def getIsLaunchAnimated(self):
        return self._getBool(16)

    def setIsLaunchAnimated(self, value):
        self._setBool(16, value)

    def getGuaranteedRewadProbability(self):
        return self._getNumber(17)

    def setGuaranteedRewadProbability(self, value):
        self._setNumber(17, value)

    def getHighRewardProbability(self):
        return self._getNumber(18)

    def setHighRewardProbability(self, value):
        self._setNumber(18, value)

    def getMediumRewardProbability(self):
        return self._getNumber(19)

    def setMediumRewardProbability(self, value):
        self._setNumber(19, value)

    def getTankRewardProbability(self):
        return self._getNumber(20)

    def setTankRewardProbability(self, value):
        self._setNumber(20, value)

    def getRentalRewardProbability(self):
        return self._getNumber(21)

    def setRentalRewardProbability(self, value):
        self._setNumber(21, value)

    def _initialize(self):
        super(WtEventPortalModel, self)._initialize()
        self._addViewModelProperty('inactivePortalAvailability', WtEventPortalAvailability())
        self._addViewModelProperty('portalAvailability', WtEventPortalAvailability())
        self._addViewModelProperty('bossSpecificRewards', UserListModel())
        self._addViewModelProperty('guaranteedRewards', UserListModel())
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('collectionReward', UserListModel())
        self._addViewModelProperty('customizationReward', UserListModel())
        self._addViewModelProperty('rewardTanks', UserListModel())
        self._addViewModelProperty('rentalTank', PortalReward())
        self._addViewModelProperty('tanks', UserListModel())
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self._addStringProperty('portalType')
        self._addStringProperty('backButtonText', '')
        self._addNumberProperty('defaultRunPortalTimes', 1)
        self._addBoolProperty('isLaunchAnimated', False)
        self._addNumberProperty('guaranteedRewadProbability', 0)
        self._addNumberProperty('highRewardProbability', 0)
        self._addNumberProperty('mediumRewardProbability', 0)
        self._addNumberProperty('tankRewardProbability', 0)
        self._addNumberProperty('rentalRewardProbability', 0)
        self.onRunPortalClick = self._addCommand('onRunPortalClick')
        self.onAnimationSettingChange = self._addCommand('onAnimationSettingChange')
        self.onUpdateLootbox = self._addCommand('onUpdateLootbox')
