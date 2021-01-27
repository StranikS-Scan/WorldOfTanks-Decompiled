# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bob/bob_entry_point_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bob.bob_entry_point_view_model import BobEntryPointViewModel
from gui.impl.pub import ViewImpl
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEventsNotificationsController, IBobAnnouncementController
if typing.TYPE_CHECKING:
    from gui.bob.bob_announcement_helpers import Announcement
_logger = logging.getLogger(__name__)

class BobEntryPointView(ViewImpl):
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __bobAnnouncement = dependency.descriptor(IBobAnnouncementController)
    __slots__ = ('__notifier', '__currentAnnouncementType')

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.bob.BobEntryPointView())
        settings.flags = flags
        settings.model = BobEntryPointViewModel()
        self.__notifier = None
        self.__currentAnnouncementType = None
        super(BobEntryPointView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BobEntryPointView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.__notificationsCtrl.onEventNotificationsChanged += self.__onEventNotificationChanged
        self.__bobAnnouncement.onAnnouncementUpdated += self.__onAnnouncementUpdated
        self.viewModel.onActionClick += self.__onClick

    def _onLoading(self, *args, **kwargs):
        super(BobEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def _finalize(self):
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__onEventNotificationChanged
        self.__bobAnnouncement.onAnnouncementUpdated -= self.__onAnnouncementUpdated
        self.viewModel.onActionClick -= self.__onClick
        self.__clearNotification()
        self.__currentAnnouncementType = None
        return

    def __onEventNotificationChanged(self, *args):
        self.__updateViewModel()

    def __onAnnouncementUpdated(self, _):
        self.__updateViewModel()

    def __updateViewModel(self):
        announcement = self.__bobAnnouncement.currentAnnouncement
        if announcement is None:
            return
        else:
            entryPointData = announcement.getEntryPointData()
            if self.__currentAnnouncementType != announcement.type:
                self.__clearNotification()
                if entryPointData.deltaFunc is not None:
                    self.__notifier = PeriodicNotifier(entryPointData.deltaFunc, self.__updateViewModel, (time_utils.ONE_MINUTE,))
                    self.__notifier.startNotification()
                self.__currentAnnouncementType = announcement.type
            with self.viewModel.transaction() as tx:
                tx.setHeader(entryPointData.header)
                tx.setBody(entryPointData.body)
                tx.setFooter(entryPointData.footer)
                tx.setState(entryPointData.state)
            return

    def __onClick(self):
        self.__bobAnnouncement.clickAnnouncement()

    def __clearNotification(self):
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clear()
            self.__notifier = None
        return
