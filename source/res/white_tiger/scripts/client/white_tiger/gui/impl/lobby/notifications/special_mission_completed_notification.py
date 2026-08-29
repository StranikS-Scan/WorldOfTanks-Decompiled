# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/notifications/special_mission_completed_notification.py
from white_tiger.gui.impl.gen.view_models.views.lobby.notifications.special_mission_completed_view_model import SpecialMissionCompletedViewModel
from gui.shared.event_dispatcher import showBadges
from gui.impl.lobby.gf_notifications import NotificationBase

class SpecialMissionCompletedNotification(NotificationBase):
    __slots__ = ()

    def __init__(self, resId, *args, **kwargs):
        model = SpecialMissionCompletedViewModel()
        super(SpecialMissionCompletedNotification, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(SpecialMissionCompletedNotification, self).getViewModel()

    def _update(self):
        with self.viewModel.transaction() as model:
            model.setIsPopUp(self._isPopUp)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onGoToBadge, self.__onGoToBadge))

    def __onClose(self):
        self.destroyWindow()

    def __onGoToBadge(self):
        showBadges()
