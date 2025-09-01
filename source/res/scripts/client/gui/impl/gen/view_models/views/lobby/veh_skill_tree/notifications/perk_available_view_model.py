# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/notifications/perk_available_view_model.py
from gui.impl.gen.view_models.common.notification_base_model import NotificationBaseModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class PerkAvailableViewModel(NotificationBaseModel):
    __slots__ = ('onClose', 'onGoToProgression')

    def __init__(self, properties=3, commands=2):
        super(PerkAvailableViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PerkAvailableViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isDisabled', False)
        self.onClose = self._addCommand('onClose')
        self.onGoToProgression = self._addCommand('onGoToProgression')
