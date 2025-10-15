# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/notification/vehicle_notification_model.py
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class VehicleNotificationModel(NotificationModel):
    __slots__ = ('onSelectVehicles',)

    def __init__(self, properties=1, commands=1):
        super(VehicleNotificationModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(VehicleNotificationModel, self)._initialize()
        self.onSelectVehicles = self._addCommand('onSelectVehicles')
