# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/SystemMessageMeta.py
from collections import namedtuple
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events
from soft_exception import SoftException

class SESSION_CONTROL_TYPE(object):
    AOGAS = 'AOGAS'
    KOREA_PARENTAL_CONTROL = 'KOREA_PARENTAL_CONTROL'


SessionControlAuxData = namedtuple('SessionControlAuxData', ('type', 'timeoutMS'))

class SystemMessageMeta(IDialogMeta):

    def __init__(self, notification):
        super(SystemMessageMeta, self).__init__()
        self.__notificationVO = notification.getListVO()
        settings = notification.getSettings()
        auxData = settings.auxData
        self.__settingsVO = {}
        if isinstance(auxData, SessionControlAuxData):
            sessionControlType = auxData.type
            self.__settingsVO['timeout'] = auxData.timeoutMS
        else:
            sessionControlType = None
        if sessionControlType == SESSION_CONTROL_TYPE.AOGAS:
            self.__title = backport.text(R.strings.aogas.NOTIFICATION.TITLE())
            self.__cancelLabel = backport.text(R.strings.aogas.NOTIFICATION.CLOSE())
        else:
            self.__title = backport.text(R.strings.messenger.serviceChannelMessages.priorityMessageTitle())
            self.__cancelLabel = backport.text(R.strings.messenger.serviceChannelMessages.buttons.close())
        return

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

    def getViewScopeType(self):
        raise SoftException('This method should not be reached in this context')
