# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_notification_panel.py
import weakref
from constants import FIRST_APRIL_ACTIONS
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control import g_sessionProvider
from gui.shared.utils.plugins import IPlugin
from helpers import i18n
_CALLBACK_NAME = 'battle.onLoadEventNotificationPanel'
_SWF_PATH = 'eventNotifications.swf'
EVENT_RANDOM = 0
EVENT_SLIDE = 1
EVENT_IMPULSE = 2
EVENT_ARTILLERY = 3
EVENT_BOUNCE = 4
EVENT_EMPTY = 5

class _EventNotificationPanel(object):

    def __init__(self, battleUI):
        self.__flashObject = weakref.proxy(battleUI.movie.eventNotificationPanel.instance)
        self.__flashObject.as_init((i18n.makeString(INGAME_GUI.EVENT_RANDOM),
         i18n.makeString(INGAME_GUI.EVENT_SLIDE),
         i18n.makeString(INGAME_GUI.EVENT_IMPULSE),
         i18n.makeString(INGAME_GUI.EVENT_ARTILLERY),
         i18n.makeString(INGAME_GUI.EVENT_BOUNCE),
         i18n.makeString(INGAME_GUI.EVENT_NOTHING)), EVENT_RANDOM, '', False)
        self.__actionIDToEventType = {FIRST_APRIL_ACTIONS.UNKNOWN: EVENT_RANDOM,
         FIRST_APRIL_ACTIONS.EMPTY: EVENT_EMPTY,
         FIRST_APRIL_ACTIONS.ARTILLERY: EVENT_ARTILLERY,
         FIRST_APRIL_ACTIONS.COMPULSE: EVENT_IMPULSE,
         FIRST_APRIL_ACTIONS.JUMP: EVENT_BOUNCE}

    def destroy(self):
        self.__flashObject = None
        self.__actionIDToEventType = {}
        return

    def update(self, eventType, timeLeft):
        if self.__flashObject is not None:
            self.__flashObject.as_updateData(self.__actionIDToEventType.get(eventType, EVENT_RANDOM), timeLeft)
        return

    def show(self, eventType, timeLeft):
        if self.__flashObject is not None:
            self.__flashObject.as_show(self.__actionIDToEventType.get(eventType, EVENT_RANDOM), timeLeft)
        return

    def hide(self):
        if self.__flashObject is not None:
            self.__flashObject.as_hide()
        return


class EventNotificationPlugin(IPlugin):

    def __init__(self, parentObj):
        super(EventNotificationPlugin, self).__init__(parentObj)
        self.__eventNotification = None
        return

    def init(self):
        super(EventNotificationPlugin, self).init()
        self._parentObj.addExternalCallback(_CALLBACK_NAME, self.__onLoad)

    def fini(self):
        self._parentObj.removeExternalCallback(_CALLBACK_NAME)
        super(EventNotificationPlugin, self).fini()

    def start(self):
        super(EventNotificationPlugin, self).start()
        self._parentObj.movie.as_loadEventPanel(_SWF_PATH)

    def stop(self):
        g_sessionProvider.getFirstOfAprilCtrl().stop()
        if self.__eventNotification is not None:
            self.__eventNotification.destroy()
            self.__eventNotification = None
        super(EventNotificationPlugin, self).stop()
        return

    def __onLoad(self, _):
        self.__eventNotification = _EventNotificationPanel(self._parentObj)
        g_sessionProvider.getFirstOfAprilCtrl().start(self.__eventNotification)
