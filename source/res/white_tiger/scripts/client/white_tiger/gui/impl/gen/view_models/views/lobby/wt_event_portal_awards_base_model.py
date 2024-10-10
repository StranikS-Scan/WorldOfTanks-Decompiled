# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_portal_awards_base_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_bonus_model import WtBonusModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_availability import WtEventPortalAvailability
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_vehicle_model import WtEventVehicleModel

class WtEventPortalAwardsBaseModel(ViewModel):
    __slots__ = ('onClose', 'onBackToPortal', 'onPreview', 'onBuy', 'onClaimReward')

    def __init__(self, properties=8, commands=5):
        super(WtEventPortalAwardsBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalAvailability(self):
        return self._getViewModel(0)

    @staticmethod
    def getPortalAvailabilityType():
        return WtEventPortalAvailability

    @property
    def rewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardsType():
        return WtBonusModel

    @property
    def additionalRewards(self):
        return self._getViewModel(2)

    @staticmethod
    def getAdditionalRewardsType():
        return WtBonusModel

    @property
    def vehicle(self):
        return self._getViewModel(3)

    @staticmethod
    def getVehicleType():
        return WtEventVehicleModel

    def getIsBoxesEnabled(self):
        return self._getBool(4)

    def setIsBoxesEnabled(self, value):
        self._setBool(4, value)

    def getAvailableLootBoxesPurchase(self):
        return self._getNumber(5)

    def setAvailableLootBoxesPurchase(self, value):
        self._setNumber(5, value)

    def getFirstLaunchReward(self):
        return self._getNumber(6)

    def setFirstLaunchReward(self, value):
        self._setNumber(6, value)

    def getIsFirstLaunch(self):
        return self._getBool(7)

    def setIsFirstLaunch(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(WtEventPortalAwardsBaseModel, self)._initialize()
        self._addViewModelProperty('portalAvailability', WtEventPortalAvailability())
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addViewModelProperty('vehicle', WtEventVehicleModel())
        self._addBoolProperty('isBoxesEnabled', True)
        self._addNumberProperty('availableLootBoxesPurchase', -1)
        self._addNumberProperty('firstLaunchReward', 100)
        self._addBoolProperty('isFirstLaunch', False)
        self.onClose = self._addCommand('onClose')
        self.onBackToPortal = self._addCommand('onBackToPortal')
        self.onPreview = self._addCommand('onPreview')
        self.onBuy = self._addCommand('onBuy')
        self.onClaimReward = self._addCommand('onClaimReward')
