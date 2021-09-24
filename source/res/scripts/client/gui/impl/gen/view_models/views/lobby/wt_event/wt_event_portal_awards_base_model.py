# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_portal_awards_base_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_bonus_model import WtBonusModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_availability import WtEventPortalAvailability
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_vehicle_model import WtEventVehicleModel

class WtEventPortalAwardsBaseModel(ViewModel):
    __slots__ = ('onClose', 'onBackToStorage', 'onPreview', 'onBuy')

    def __init__(self, properties=5, commands=4):
        super(WtEventPortalAwardsBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def portalAvailability(self):
        return self._getViewModel(0)

    @property
    def additionalRewards(self):
        return self._getViewModel(1)

    @property
    def vehicle(self):
        return self._getViewModel(2)

    def getIsBoxesEnabled(self):
        return self._getBool(3)

    def setIsBoxesEnabled(self, value):
        self._setBool(3, value)

    def getAvailableLootBoxesPurchase(self):
        return self._getNumber(4)

    def setAvailableLootBoxesPurchase(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(WtEventPortalAwardsBaseModel, self)._initialize()
        self._addViewModelProperty('portalAvailability', WtEventPortalAvailability())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addViewModelProperty('vehicle', WtEventVehicleModel())
        self._addBoolProperty('isBoxesEnabled', True)
        self._addNumberProperty('availableLootBoxesPurchase', -1)
        self.onClose = self._addCommand('onClose')
        self.onBackToStorage = self._addCommand('onBackToStorage')
        self.onPreview = self._addCommand('onPreview')
        self.onBuy = self._addCommand('onBuy')
