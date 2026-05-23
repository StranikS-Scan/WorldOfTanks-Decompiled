# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/notification/decorators.py
from __future__ import absolute_import
from gui.shared.notifications import NotificationGroup, NotificationGuiSettings
from helpers import dependency
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE, NOTIFICATION_TYPE
from open_bundle.gui.constants import GFNotificationTemplates
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController

class OpenBundleStartDecorator(MessageDecorator):

    def __init__(self, entityID, model=None, data=None):
        super(OpenBundleStartDecorator, self).__init__(entityID, self.__makeEntity(data), self.__makeSettings(), model)

    def getGroup(self):
        return NotificationGroup.INFO

    def getType(self):
        return NOTIFICATION_TYPE.OPEN_BUNDLE_ENTRY

    @staticmethod
    def __makeEntity(data):
        return g_settings.msgTemplates.format(data['template'], data={'linkageData': data['data']})

    @staticmethod
    def __makeSettings():
        return NotificationGuiSettings(isNotify=True, priorityLevel=g_settings.msgTemplates.priority(GFNotificationTemplates.START_NOTIFICATION))


class OpenBundleReminderDecorator(MessageDecorator):
    __openBundle = dependency.descriptor(IOpenBundleController)
    __ENTITY_ID = 0

    def __init__(self, message, savedData, model):
        super(OpenBundleReminderDecorator, self).__init__(self.__ENTITY_ID, self.__makeEntity(message, savedData), self.__makeSettings(), model)

    def getSavedData(self):
        return self._entity.get('savedData', {})

    def _getEvents(self):
        return ((self.__openBundle.onStatusChanged, self.__update), (self.__openBundle.onSettingsChanged, self.__update))

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(OpenBundleReminderDecorator, self)._make(formatted, settings)

    def __makeEntity(self, message, savedData):
        return g_settings.msgTemplates.format('OpenBundleReminderSysMessage', ctx=message, data={'savedData': savedData})

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, priorityLevel=g_settings.msgTemplates.priority('OpenBundleReminderSysMessage'))

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            self._entity['buttonsStates'] = {'submit': NOTIFICATION_BUTTON_STATE.DEFAULT if self.__openBundle.isBundleActive(self.getSavedData().get('bundleID')) else NOTIFICATION_BUTTON_STATE.VISIBLE}
            return

    def __update(self, *_):
        self.__updateEntityButtons()
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return
