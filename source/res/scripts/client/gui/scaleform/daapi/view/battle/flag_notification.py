# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/flag_notification.py
import weakref
from gui import makeHtmlString
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from debug_utils import LOG_ERROR
from gui.battle_control import g_sessionProvider
from gui.shared.utils.plugins import IPlugin
from helpers import i18n

class _FlagNotification:

    class __NOTIFICATION_TYPE:
        FLAG_CAPTURED = 'flagCaptured'
        FLAG_DROPPED = 'flagDropped'
        FLAG_DELIVERED = 'flagDelivered'

    def __init__(self, battleUI):
        self.__flashObject = weakref.proxy(battleUI.movie.flagNotification.instance)
        self.__notificationsByType = {self.__NOTIFICATION_TYPE.FLAG_CAPTURED: {'title': i18n.makeString(INGAME_GUI.FLAGNOTIFICATION_FLAGCAPTURED),
                                                  'message': i18n.makeString(INGAME_GUI.FLAGNOTIFICATION_FLAGINBASE)},
         self.__NOTIFICATION_TYPE.FLAG_DELIVERED: {'title': '',
                                                   'message': i18n.makeString(INGAME_GUI.FLAGNOTIFICATION_FLAGDELIVERED)},
         self.__NOTIFICATION_TYPE.FLAG_DROPPED: {'title': None,
                                                 'message': None}}
        return

    def destroy(self):
        self.__flashObject = None
        self.__notificationsByType = None
        return

    @property
    def flashObject(self):
        return self.__flashObject

    def showFlagCaptured(self):
        self.__showMsgByType(self.__NOTIFICATION_TYPE.FLAG_CAPTURED)

    def showFlagDelivered(self):
        self.__showMsgByType(self.__NOTIFICATION_TYPE.FLAG_DELIVERED)

    def showFlagDropped(self):
        self.__showMsgByType(self.__NOTIFICATION_TYPE.FLAG_DROPPED)

    def __showMsgByType(self, typeID):
        if typeID in self.__notificationsByType:
            notifications = self.__notificationsByType[typeID]
            self.__showMsg(typeID, notifications['title'], notifications['message'])
        else:
            LOG_ERROR('No such msgType: ', typeID)

    def __showMsg(self, type, title, msg):
        if self.__flashObject is not None:
            self.__flashObject.as_showNotification(type, title, msg)
        return


class FlagNotificationPlugin(IPlugin):
    __CALLBACK_NAME = 'battle.onLoadFlagNotification'

    def __init__(self, parentObj):
        super(FlagNotificationPlugin, self).__init__(parentObj)
        self.__flagNotification = None
        return

    def init(self):
        super(FlagNotificationPlugin, self).init()
        self._parentObj.addExternalCallback(self.__CALLBACK_NAME, self.__onLoad)

    def fini(self):
        self._parentObj.removeExternalCallback(self.__CALLBACK_NAME)
        super(FlagNotificationPlugin, self).fini()

    def start(self):
        super(FlagNotificationPlugin, self).start()
        self._parentObj.movie.loadFlagNotification()

    def stop(self):
        g_sessionProvider.getNotificationsCtrl().stop()
        if self.__flagNotification is not None:
            self.__flagNotification.destroy()
            self.__flagNotification = None
        super(FlagNotificationPlugin, self).stop()
        return

    def __onLoad(self, _):
        self.__flagNotification = _FlagNotification(self._parentObj)
        g_sessionProvider.getNotificationsCtrl().start(self.__flagNotification)
