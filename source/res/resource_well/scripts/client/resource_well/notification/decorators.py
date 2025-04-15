# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/notification/decorators.py
from gui.shared.notifications import NotificationGuiSettings, NotificationPriorityLevel
from helpers import dependency
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_TYPE, NOTIFICATION_BUTTON_STATE
from skeletons.gui.resource_well import IResourceWellController

class ResourceWellLockButtonDecorator(MessageDecorator):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(ResourceWellLockButtonDecorator, self).__init__(entityID, entity, settings, model)
        self.__resourceWell.onEventUpdated += self.__update
        self.__resourceWell.onSettingsChanged += self.__update

    def clear(self):
        self.__resourceWell.onEventUpdated -= self.__update
        self.__resourceWell.onSettingsChanged -= self.__update

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(ResourceWellLockButtonDecorator, self)._make(formatted, settings)

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            if self.__resourceWell.isActive():
                state = NOTIFICATION_BUTTON_STATE.DEFAULT
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
            self._entity['buttonsStates'] = {'submit': state}
            return

    def __update(self, *_):
        self.__updateEntityButtons()
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return


class ResourceWellStartDecorator(ResourceWellLockButtonDecorator):

    def __init__(self, entityID, message, model):
        super(ResourceWellStartDecorator, self).__init__(entityID, self.__makeEntity(message), self.__makeSettings(), model)

    def getType(self):
        return NOTIFICATION_TYPE.RESOURCE_WELL_START

    def __makeEntity(self, message):
        return g_settings.msgTemplates.format('ResourceWellStartSysMessage', ctx=message)

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.HIGH)
