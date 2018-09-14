# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/flag_notification.py
import weakref
from debug_utils import LOG_ERROR
from gui.battle_control import g_sessionProvider
from gui.shared.utils.plugins import IPlugin
from helpers import i18n

class _NOTIFICATION_TYPE:
    FLAG_CAPTURED = 0
    FLAG_DROPPED = 1
    FLAG_DELIVERED = 2
    FLAG_ABSORBED = 3


_CALLBACK_NAME = 'battle.onLoadFlagNotification'

class _FlagNotification(object):

    def __init__(self, battleUI):
        self.__flashObject = weakref.proxy(battleUI.movie.flagNotification.instance)
        self.__notificationsByType = {_NOTIFICATION_TYPE.FLAG_CAPTURED: {'type': 'flagCaptured',
                                            'title': i18n.makeString('#ingame_gui:flagNotification/flagCaptured'),
                                            'message': i18n.makeString('#ingame_gui:flagNotification/flagInbase')},
         _NOTIFICATION_TYPE.FLAG_DELIVERED: {'type': 'flagDelivered',
                                             'title': i18n.makeString('#ingame_gui:flagNotification/flagDelivered'),
                                             'message': ''},
         _NOTIFICATION_TYPE.FLAG_ABSORBED: {'type': 'flagDelivered',
                                            'title': i18n.makeString('#ingame_gui:flagNotification/flagAbsorbed'),
                                            'message': ''},
         _NOTIFICATION_TYPE.FLAG_DROPPED: {'type': 'flagDropped',
                                           'title': None,
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
        self.__showMsgByType(_NOTIFICATION_TYPE.FLAG_CAPTURED)

    def showFlagDelivered(self):
        self.__showMsgByType(_NOTIFICATION_TYPE.FLAG_DELIVERED)

    def showFlagAbsorbed(self):
        self.__showMsgByType(_NOTIFICATION_TYPE.FLAG_ABSORBED)

    def showFlagDropped(self):
        self.__showMsgByType(_NOTIFICATION_TYPE.FLAG_DROPPED)

    def __showMsgByType(self, typeID):
        if typeID in self.__notificationsByType:
            notifications = self.__notificationsByType[typeID]
            self.__showMsg(notifications['type'], notifications['title'], notifications['message'])
        else:
            LOG_ERROR('No such msgType: ', typeID)

    def __showMsg(self, type, title, msg):
        if self.__flashObject is not None:
            self.__flashObject.as_showNotification(type, title, msg)
        return


class FlagNotificationPlugin(IPlugin):

    def __init__(self, parentObj):
        super(FlagNotificationPlugin, self).__init__(parentObj)
        self.__flagNotification = None
        return

    def init(self):
        super(FlagNotificationPlugin, self).init()
        self._parentObj.addExternalCallback(_CALLBACK_NAME, self.__onLoad)

    def fini(self):
        self._parentObj.removeExternalCallback(_CALLBACK_NAME)
        super(FlagNotificationPlugin, self).fini()

    def start(self):
        super(FlagNotificationPlugin, self).start()
        self._parentObj.movie.falloutItems.as_loadFlagNotification()

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
