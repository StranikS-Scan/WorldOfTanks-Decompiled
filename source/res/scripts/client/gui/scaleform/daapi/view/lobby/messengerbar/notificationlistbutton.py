# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/NotificationListButton.py
from gui.Scaleform.daapi.view.meta.NotificationListButtonMeta import NotificationListButtonMeta
from helpers import dependency
from notification import NotificationMVC
from gui.shared.formatters import text_styles
from skeletons.account_helpers.settings_core import ISettingsCore

class NotificationListButton(NotificationListButtonMeta):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('__notifyMessagesCount',)

    def __init__(self):
        super(NotificationListButton, self).__init__()
        self.__notifyMessagesCount = 0
        NotificationMVC.g_instance.getModel().onNotifiedMessagesCountChanged += self.__notifiedMessagesCountChangeHandler

    def _populate(self):
        super(NotificationListButton, self)._populate()
        self.__settingsCore.interfaceScale.onScaleChanged += self.__scaleChangeHandler
        self.__setState(NotificationMVC.g_instance.getModel().getNotifiedMessagesCount())

    def handleClick(self):
        NotificationMVC.g_instance.getModel().setListDisplayState()

    def _dispose(self):
        self.__settingsCore.interfaceScale.onScaleChanged -= self.__scaleChangeHandler
        model = NotificationMVC.g_instance.getModel()
        if model:
            model.onNotifiedMessagesCountChanged -= self.__notifiedMessagesCountChangeHandler
        super(NotificationListButton, self)._dispose()

    def __notifiedMessagesCountChangeHandler(self, notifyMessagesCount):
        self.__setState(notifyMessagesCount)

    def __scaleChangeHandler(self, _):
        self.__setState(self.__notifyMessagesCount)

    def __setState(self, count):
        self.__notifyMessagesCount = count
        counterValue = ''
        if count > 0:
            counterValue = text_styles.counterLabelText(str(count))
        self.as_setStateS(count > 0, counterValue)
