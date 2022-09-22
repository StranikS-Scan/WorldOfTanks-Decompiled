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


class EventTankType(Enum):
    PRIMARY = 'R121_KV4_KTT'
    SECONDARY = 'GB110_FV4201_Chieftain_Prototype'


class WtEventPortalModel(WtEventPortalsBase):
    __slots__ = ('onRunPortalClick', 'onBackButtonClick', 'onPreviewTankClick', 'onAnimationSettingChange')

    def __init__(self, properties=17, commands=6):
        super(WtEventPortalModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalAvailability(self):
        return self._getViewModel(2)

    @staticmethod
    def getPortalAvailabilityType():
        return WtEventPortalAvailability

    @property
    def rewards(self):
        return self._getViewModel(3)

    @staticmethod
    def getRewardsType():
        return PortalReward

    @property
    def collectionReward(self):
        return self._getViewModel(4)

    @staticmethod
    def getCollectionRewardType():
        return PortalReward

    @property
    def customizationReward(self):
        return self._getViewModel(5)

    @staticmethod
    def getCustomizationRewardType():
        return PortalReward

    @property
    def rewardTanks(self):
        return self._getViewModel(6)

    @staticmethod
    def getRewardTanksType():
        return TankReward

    @property
    def rentalTank(self):
        return self._getViewModel(7)

    @staticmethod
    def getRentalTankType():
        return PortalReward

    @property
    def tanks(self):
        return self._getViewModel(8)

    @staticmethod
    def getTanksType():
        return PortalPremiumTanks

    @property
    def guaranteedAward(self):
        return self._getViewModel(9)

    @staticmethod
    def getGuaranteedAwardType():
        return WtEventGuaranteedAward

    def getPortalType(self):
        return PortalType(self._getString(10))

    def setPortalType(self, value):
        self._setString(10, value.value)

    def getBackButtonText(self):
        return self._getString(11)

    def setBackButtonText(self, value):
        self._setString(11, value)

    def getDefaultRunPortalTimes(self):
        return self._getNumber(12)

    def setDefaultRunPortalTimes(self, value):
        self._setNumber(12, value)

    def getFirstLaunchReward(self):
        return self._getNumber(13)

    def setFirstLaunchReward(self, value):
        self._setNumber(13, value)

    def getPrimaryEventTank(self):
        return EventTankType(self._getString(14))

    def setPrimaryEventTank(self, value):
        self._setString(14, value.value)

    def getSecondaryEventTank(self):
        return EventTankType(self._getString(15))

    def setSecondaryEventTank(self, value):
        self._setString(15, value.value)

    def getIsLaunchAnimated(self):
        return self._getBool(16)

    def setIsLaunchAnimated(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(WtEventPortalModel, self)._initialize()
        self._addViewModelProperty('portalAvailability', WtEventPortalAvailability())
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('collectionReward', PortalReward())
        self._addViewModelProperty('customizationReward', UserListModel())
        self._addViewModelProperty('rewardTanks', UserListModel())
        self._addViewModelProperty('rentalTank', PortalReward())
        self._addViewModelProperty('tanks', UserListModel())
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self._addStringProperty('portalType')
        self._addStringProperty('backButtonText', '')
        self._addNumberProperty('defaultRunPortalTimes', 1)
        self._addNumberProperty('firstLaunchReward', 100)
        self._addStringProperty('primaryEventTank')
        self._addStringProperty('secondaryEventTank')
        self._addBoolProperty('isLaunchAnimated', False)
        self.onRunPortalClick = self._addCommand('onRunPortalClick')
        self.onBackButtonClick = self._addCommand('onBackButtonClick')
        self.onPreviewTankClick = self._addCommand('onPreviewTankClick')
        self.onAnimationSettingChange = self._addCommand('onAnimationSettingChange')
