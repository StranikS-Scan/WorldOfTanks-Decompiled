# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/SystemMessageMeta.py
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.Scaleform.locale.AOGAS import AOGAS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.shared import events
from web_stubs import i18n

class SystemMessageMeta(IDialogMeta):
    AOGAS = 'AOGAS'

    def __init__(self, notification):
        super(SystemMessageMeta, self).__init__()
        self.__notificationVO = notification.getListVO()
        settings = notification.getSettings()
        auxData = settings.auxData
        if len(auxData) > 1 and auxData[0] == self.AOGAS:
            self.__settingsVO = {'timeout': auxData[1]}
            self.__title = i18n.makeString(AOGAS.NOTIFICATION_TITLE)
            self.__cancelLabel = i18n.makeString(AOGAS.NOTIFICATION_CLOSE)
        else:
            self.__settingsVO = {}
            self.__title = i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_PRIORITYMESSAGETITLE)
            self.__cancelLabel = i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_BUTTONS_CLOSE)

    def getSettings(self):
        return self.__settingsVO

    def getMessageObject(self):
        return self.__notificationVO

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_SYSTEM_MESSAGE_DIALOG

    def getTitle(self):
        return self.__title

    def getCancelLabel(self):
        return self.__cancelLabel

    def cleanUp(self):
        self.__notificationVO = None
        self.__settingsVO = None
        return
