# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/notification/listeners.py
from __future__ import absolute_import
import uuid
from gui.impl import backport
from gui.impl.lobby.gf_notifications.cache import getCache
from helpers import dependency
from helpers.time_utils import getServerUTCTime, makeLocalServerTime, ONE_DAY
from messenger.formatters import TimeFormatter
from notification.listeners import _NotificationListener
from open_bundle.gui.constants import GFNotificationTemplates
from open_bundle.helpers.account_settings import isReminderNotificationShown, isStartNotificationShown, setReminderNotificationShown
from open_bundle.helpers.resources import getTextResource
from open_bundle.notification.decorators import OpenBundleStartDecorator, OpenBundleReminderDecorator
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController

class OpenBundleListener(_NotificationListener):
    __openBundle = dependency.descriptor(IOpenBundleController)
    __ENTITY_ID = 0

    def __init__(self):
        super(OpenBundleListener, self).__init__()
        self.__openingCtx = {}

    def start(self, model):
        result = super(OpenBundleListener, self).start(model)
        self.__openBundle.onStatusChanged += self.__onStatusChanged
        self.__openBundle.onSettingsChanged += self.__tryNotify
        if result:
            self.__tryNotify()
        return True

    def stop(self):
        self.__openBundle.onSettingsChanged -= self.__tryNotify
        self.__openBundle.onStatusChanged -= self.__onStatusChanged
        super(OpenBundleListener, self).stop()

    def __tryNotify(self):
        for bundleID in self.__openBundle.bundleIDs:
            self.__pushEventNotification(bundleID)

    def __onStatusChanged(self, bundleID):
        self.__pushEventNotification(bundleID)

    def __pushEventNotification(self, bundleID):
        if self.__openBundle.isBundleActive(bundleID) and not self.__openBundle.isAllBundleCellsReceived(bundleID):
            finishTime = self.__openBundle.getBundle(bundleID).finish
            if not isStartNotificationShown(bundleID):
                self.__pushStartNotification(bundleID)
            if finishTime > getServerUTCTime() > finishTime - ONE_DAY and not isReminderNotificationShown(bundleID):
                self.__pushReminderNotification(bundleID)

    def __pushStartNotification(self, bundleID):
        model = self._model()
        if model is not None:
            gfDataID = str(uuid.uuid4())
            getCache().setPayload(gfDataID, {'bundleID': bundleID})
            model.addNotification(OpenBundleStartDecorator(entityID=self.__ENTITY_ID, model=model, data={'data': {'gfDataID': gfDataID},
             'template': GFNotificationTemplates.START_NOTIFICATION}))
        return

    def __pushReminderNotification(self, bundleID):
        model = self._model()
        if model is not None:
            localFinishTime = makeLocalServerTime(self.__openBundle.getBundle(bundleID).finish)
            eventName = backport.text(getTextResource(bundleID, ('bundle', 'name'))())
            messageData = {'header': backport.text(getTextResource(bundleID, ('serviceChannelMessages', 'reminder', 'header'))(), eventName=eventName),
             'text': backport.text(getTextResource(bundleID, ('serviceChannelMessages', 'reminder', 'text'))(), date=TimeFormatter.getShortDateFormat(localFinishTime))}
            model.addNotification(OpenBundleReminderDecorator(message=messageData, model=model, savedData={'bundleID': bundleID}))
            setReminderNotificationShown(bundleID)
        return
