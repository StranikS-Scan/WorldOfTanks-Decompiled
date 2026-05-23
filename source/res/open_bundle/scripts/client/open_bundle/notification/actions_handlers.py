# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/notification/actions_handlers.py
from __future__ import absolute_import
from notification.actions_handlers import NavigationDisabledActionHandler
from notification.settings import NOTIFICATION_TYPE
from open_bundle.gui.shared.event_dispatcher import showOpenBundleMainView

class OpenBundleReminderHandler(NavigationDisabledActionHandler):

    @classmethod
    def getNotType(cls):
        return NOTIFICATION_TYPE.MESSAGE

    @classmethod
    def getActions(cls):
        pass

    def doAction(self, model, entityID, action):
        notification = model.getNotification(self.getNotType(), entityID)
        savedData = notification.getSavedData()
        if savedData and 'bundleID' in savedData and savedData['bundleID']:
            showOpenBundleMainView(savedData['bundleID'])
