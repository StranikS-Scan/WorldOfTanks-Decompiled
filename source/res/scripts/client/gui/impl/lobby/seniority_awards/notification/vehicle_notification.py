# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/notification/vehicle_notification.py
from gui.impl.gen.view_models.views.lobby.seniority_awards.notification.vehicle_notification_model import VehicleNotificationModel
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from gui.shared.event_dispatcher import showSeniorityVehicleSelectorWindow

class VehicleNotification(NotificationBase):
    __slots__ = ()

    def __init__(self, resId, *args, **kwargs):
        model = VehicleNotificationModel()
        super(VehicleNotification, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(VehicleNotification, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleNotification, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsPopUp(self._isPopUp)

    def _getEvents(self):
        return ((self.viewModel.onSelectVehicles, self.__onSelectVehicles),)

    def __onSelectVehicles(self):
        showSeniorityVehicleSelectorWindow(self._linkageData.toDict()['giftToken'])
