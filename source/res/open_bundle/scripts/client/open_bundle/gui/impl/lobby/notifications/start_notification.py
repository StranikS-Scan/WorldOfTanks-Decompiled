# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/notifications/start_notification.py
from __future__ import absolute_import
from helpers import dependency
from open_bundle.gui.impl.gen.view_models.views.lobby.notifications.start_notification_model import StartNotificationModel
from open_bundle.gui.shared.event_dispatcher import showOpenBundleMainView
from open_bundle.helpers.account_settings import setStartNotificationShown
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase

class StartNotification(NotificationBase):
    __openBundle = dependency.descriptor(IOpenBundleController)

    def __init__(self, resId, *args, **kwargs):
        super(StartNotification, self).__init__(resId, StartNotificationModel(), *args, **kwargs)

    @property
    def viewModel(self):
        return super(StartNotification, self).getViewModel()

    @property
    def bundleID(self):
        return self._getPayload()['bundleID']

    def _getEvents(self):
        return super(StartNotification, self)._getEvents() + ((self.__openBundle.onSettingsChanged, self.__onSettingsChanged), (self.__openBundle.onStatusChanged, self.__onStatusChanged), (self.viewModel.onOpenBundle, self.__onOpenBundle))

    def _canNavigate(self):
        return super(StartNotification, self)._canNavigate() and self.__openBundle.isBundleActive(self.bundleID)

    def _update(self):
        with self.viewModel.transaction() as tx:
            tx.setIsPopUp(self._isPopUp)
            tx.setIsButtonDisabled(not self._canNavigate())
            tx.setBundleID(self.bundleID)
            tx.setBundleType(self.__openBundle.getBundle(self.bundleID).type)
        setStartNotificationShown(self.bundleID)

    def __onSettingsChanged(self):
        self.viewModel.setIsButtonDisabled(not self._canNavigate())

    def __onStatusChanged(self, bundleID):
        if bundleID == self.bundleID:
            self.viewModel.setIsButtonDisabled(not self._canNavigate())

    def __onOpenBundle(self):
        if self._canNavigate():
            showOpenBundleMainView(self.bundleID)
