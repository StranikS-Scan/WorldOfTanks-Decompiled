# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_portal_model.py
from enum import Enum
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_premium_tanks import PortalPremiumTanks
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_reward import PortalReward
from white_tiger.gui.impl.gen.view_models.views.lobby.tank_reward import TankReward
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_guaranteed_award import WtEventGuaranteedAward
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_availability import WtEventPortalAvailability
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portals_base import WtEventPortalsBase

class PortalType(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'
    TANK = 'tank'


class LootBoxType(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'
    TANK = 'tank'


class EventTankType(Enum):
    PRIMARY = 'G168_KJpz_T_III'
    SECONDARY = 'R212_Object_265T'
    MAIN = 'Pl26_Czolg_P_Wz_46'
    BOSS = 'Pl26_Czolg_P_Wz_46_Verbesserter'


class WtEventPortalModel(WtEventPortalsBase):
    __slots__ = ('onRunPortalClick', 'onBackButtonClick', 'onAnimationSettingChange')

    def __init__(self, properties=28, commands=5):
        super(WtEventPortalModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalAvailability(self):
        return self._getViewModel(10)

    @staticmethod
    def getPortalAvailabilityType():
        return WtEventPortalAvailability

    @property
    def rewards(self):
        return self._getViewModel(11)

    @staticmethod
    def getRewardsType():
        return PortalReward

    @property
    def collectionReward(self):
        return self._getViewModel(12)

    @staticmethod
    def getCollectionRewardType():
        return PortalReward

    @property
    def customizationReward(self):
        return self._getViewModel(13)

    @staticmethod
    def getCustomizationRewardType():
        return PortalReward

    @property
    def rewardTanks(self):
        return self._getViewModel(14)

    @staticmethod
    def getRewardTanksType():
        return PortalReward

    @property
    def rewardTank(self):
        return self._getViewModel(15)

    @staticmethod
    def getRewardTankType():
        return TankReward

    @property
    def tanks(self):
        return self._getViewModel(16)

    @staticmethod
    def getTanksType():
        return PortalPremiumTanks

    @property
    def guaranteedAward(self):
        return self._getViewModel(17)

    @staticmethod
    def getGuaranteedAwardType():
        return WtEventGuaranteedAward

    def getPortalType(self):
        return PortalType(self._getString(18))

    def setPortalType(self, value):
        self._setString(18, value.value)

    def getBackButtonText(self):
        return self._getString(19)

    def setBackButtonText(self, value):
        self._setString(19, value)

    def getDefaultRunPortalTimes(self):
        return self._getNumber(20)

    def setDefaultRunPortalTimes(self, value):
        self._setNumber(20, value)

    def getFirstLaunchReward(self):
        return self._getNumber(21)

    def setFirstLaunchReward(self, value):
        self._setNumber(21, value)

    def getPrimaryEventTank(self):
        return EventTankType(self._getString(22))

    def setPrimaryEventTank(self, value):
        self._setString(22, value.value)

    def getSecondaryEventTank(self):
        return EventTankType(self._getString(23))

    def setSecondaryEventTank(self, value):
        self._setString(23, value.value)

    def getIsLaunchAnimated(self):
        return self._getBool(24)

    def setIsLaunchAnimated(self, value):
        self._setBool(24, value)

    def getRewardsProbability(self):
        return self._getNumber(25)

    def setRewardsProbability(self, value):
        self._setNumber(25, value)

    def getCustomizationProbability(self):
        return self._getNumber(26)

    def setCustomizationProbability(self, value):
        self._setNumber(26, value)

    def getTanksProbability(self):
        return self._getNumber(27)

    def setTanksProbability(self, value):
        self._setNumber(27, value)

    def _initialize(self):
        super(WtEventPortalModel, self)._initialize()
        self._addViewModelProperty('portalAvailability', WtEventPortalAvailability())
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('collectionReward', UserListModel())
        self._addViewModelProperty('customizationReward', UserListModel())
        self._addViewModelProperty('rewardTanks', UserListModel())
        self._addViewModelProperty('rewardTank', TankReward())
        self._addViewModelProperty('tanks', UserListModel())
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self._addStringProperty('portalType')
        self._addStringProperty('backButtonText', '')
        self._addNumberProperty('defaultRunPortalTimes', 1)
        self._addNumberProperty('firstLaunchReward', 100)
        self._addStringProperty('primaryEventTank')
        self._addStringProperty('secondaryEventTank')
        self._addBoolProperty('isLaunchAnimated', False)
        self._addNumberProperty('rewardsProbability', 0)
        self._addNumberProperty('customizationProbability', 0)
        self._addNumberProperty('tanksProbability', 0)
        self.onRunPortalClick = self._addCommand('onRunPortalClick')
        self.onBackButtonClick = self._addCommand('onBackButtonClick')
        self.onAnimationSettingChange = self._addCommand('onAnimationSettingChange')
