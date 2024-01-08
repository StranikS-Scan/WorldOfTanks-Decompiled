# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/notification/lootbox_decorator.py
from skeletons.gui.game_control import IGuiLootBoxesController
from helpers import dependency
from notification.decorators import MessageDecorator
from messenger import g_settings
from gui.shared.notifications import NotificationGuiSettings, NotificationPriorityLevel
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons, text_styles
from notification.settings import NOTIFICATION_BUTTON_STATE

class EventLootBoxesDecorator(MessageDecorator):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, entityID, message, model):
        super(EventLootBoxesDecorator, self).__init__(entityID, self.__makeEntity(message), self.__makeSettings(), model)
        self.__guiLootBoxes.onStatusChange += self.__update
        self.__guiLootBoxes.onAvailabilityChange += self.__update

    def clear(self):
        self.__guiLootBoxes.onStatusChange -= self.__update
        self.__guiLootBoxes.onAvailabilityChange -= self.__update

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(EventLootBoxesDecorator, self)._make(formatted, settings)

    def __makeEntity(self, message):
        return g_settings.msgTemplates.format('EventLootBoxStartSysMessage', ctx=message)

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.MEDIUM)

    def __updateEntityButtons(self):
        if self._entity is None or not self._entity.get('buttonsLayout'):
            return
        else:
            labelText = backport.text(R.strings.lootboxes.notification.eventStart.button())
            if self.__guiLootBoxes.useExternalShop():
                labelText = text_styles.concatStylesWithSpace(labelText, icons.webLink())
            self._entity['buttonsLayout'][0]['label'] = labelText
            if self.__guiLootBoxes.isEnabled() and self.__guiLootBoxes.isLootBoxesAvailable():
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
