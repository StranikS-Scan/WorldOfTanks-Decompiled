# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_portal_model.py
from enum import Enum
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.portal_premium_tanks import PortalPremiumTanks
from gui.impl.gen.view_models.views.lobby.wt_event.portal_reward import PortalReward
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_guaranteed_award import WtEventGuaranteedAward
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_availability import WtEventPortalAvailability
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portals_base import WtEventPortalsBase
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_vehicle_model import WtEventVehicleModel

class PortalType(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'
    TANK = 'tank'


class LootBoxType(Enum):
    HUNTER = 'hunter'
    BOSS = 'boss'


class WtEventPortalModel(WtEventPortalsBase):
    __slots__ = ('onRunPortalClick', 'onBackButtonClick', 'onPreviewTankClick')

    def __init__(self, properties=13, commands=5):
        super(WtEventPortalModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalAvailability(self):
        return self._getViewModel(3)

    @property
    def rewards(self):
        return self._getViewModel(4)

    @property
    def collectionReward(self):
        return self._getViewModel(5)

    @property
    def specialTankBonus(self):
        return self._getViewModel(6)

    @property
    def specialTank(self):
        return self._getViewModel(7)

    @property
    def tanks(self):
        return self._getViewModel(8)

    @property
    def guaranteedAward(self):
        return self._getViewModel(9)

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

    def _initialize(self):
        super(WtEventPortalModel, self)._initialize()
        self._addViewModelProperty('portalAvailability', WtEventPortalAvailability())
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('collectionReward', PortalReward())
        self._addViewModelProperty('specialTankBonus', PortalReward())
        self._addViewModelProperty('specialTank', WtEventVehicleModel())
        self._addViewModelProperty('tanks', UserListModel())
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self._addStringProperty('portalType')
        self._addStringProperty('backButtonText', '')
        self._addNumberProperty('defaultRunPortalTimes', 1)
        self.onRunPortalClick = self._addCommand('onRunPortalClick')
        self.onBackButtonClick = self._addCommand('onBackButtonClick')
        self.onPreviewTankClick = self._addCommand('onPreviewTankClick')
