# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_portal_model.py
from enum import Enum
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.main_vehicle_prize import MainVehiclePrize
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
    PRIMARY = 'A33_MTLS_1G14'
    SECONDARY = 'GB113_Matilda_LVT'
    MAIN = 'G36_PzII_J'
    BOSS = 'R33_Churchill_LL'


class WtEventPortalModel(WtEventPortalsBase):
    __slots__ = ('onRunPortalClick', 'onBackButtonClick', 'onPreviewTankClick', 'onAnimationSettingChange')

    def __init__(self, properties=26, commands=6):
        super(WtEventPortalModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalAvailability(self):
        return self._getViewModel(7)

    @staticmethod
    def getPortalAvailabilityType():
        return WtEventPortalAvailability

    @property
    def rewards(self):
        return self._getViewModel(8)

    @staticmethod
    def getRewardsType():
        return PortalReward

    @property
    def collectionReward(self):
        return self._getViewModel(9)

    @staticmethod
    def getCollectionRewardType():
        return PortalReward

    @property
    def customizationReward(self):
        return self._getViewModel(10)

    @staticmethod
    def getCustomizationRewardType():
        return PortalReward

    @property
    def rewardTanks(self):
        return self._getViewModel(11)

    @staticmethod
    def getRewardTanksType():
        return TankReward

    @property
    def rewardTank(self):
        return self._getViewModel(12)

    @staticmethod
    def getRewardTankType():
        return TankReward

    @property
    def tanks(self):
        return self._getViewModel(13)

    @staticmethod
    def getTanksType():
        return PortalPremiumTanks

    @property
    def guaranteedAward(self):
        return self._getViewModel(14)

    @staticmethod
    def getGuaranteedAwardType():
        return WtEventGuaranteedAward

    @property
    def mainVehiclePrize(self):
        return self._getViewModel(15)

    @staticmethod
    def getMainVehiclePrizeType():
        return MainVehiclePrize

    def getPortalType(self):
        return PortalType(self._getString(16))

    def setPortalType(self, value):
        self._setString(16, value.value)

    def getBackButtonText(self):
        return self._getString(17)

    def setBackButtonText(self, value):
        self._setString(17, value)

    def getDefaultRunPortalTimes(self):
        return self._getNumber(18)

    def setDefaultRunPortalTimes(self, value):
        self._setNumber(18, value)

    def getFirstLaunchReward(self):
        return self._getNumber(19)

    def setFirstLaunchReward(self, value):
        self._setNumber(19, value)

    def getPrimaryEventTank(self):
        return EventTankType(self._getString(20))

    def setPrimaryEventTank(self, value):
        self._setString(20, value.value)

    def getSecondaryEventTank(self):
        return EventTankType(self._getString(21))

    def setSecondaryEventTank(self, value):
        self._setString(21, value.value)

    def getIsLaunchAnimated(self):
        return self._getBool(22)

    def setIsLaunchAnimated(self, value):
        self._setBool(22, value)

    def getRewardsProbability(self):
        return self._getNumber(23)

    def setRewardsProbability(self, value):
        self._setNumber(23, value)

    def getCustomizationProbability(self):
        return self._getNumber(24)

    def setCustomizationProbability(self, value):
        self._setNumber(24, value)

    def getTanksProbability(self):
        return self._getNumber(25)

    def setTanksProbability(self, value):
        self._setNumber(25, value)

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
        self._addViewModelProperty('mainVehiclePrize', MainVehiclePrize())
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
        self.onPreviewTankClick = self._addCommand('onPreviewTankClick')
        self.onAnimationSettingChange = self._addCommand('onAnimationSettingChange')
