# Embedded file name: scripts/client/gui/Scaleform/SystemMessagesInterface.py
import time
import account_helpers
from ConnectionManager import connectionManager
import constants
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import game_control, GUI_SETTINGS
from gui.shared import g_itemsCache
from helpers import i18n
from gui.SystemMessages import SM_TYPE, BaseSystemMessages
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from PlayerEvents import g_playerEvents
from MemoryCriticalController import g_critMemHandler
from adisp import process
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
KOREA_TIME_TILL_MIDNIGHT = 7200

class SystemMessagesInterface(BaseSystemMessages):
    __CMD_BLOCK_PREFIX = 'cmd_'
    __PROMO_BLOCK_PREFIX = 'promo_'

    def init(self):
        connectionManager.onConnected += self.__onConnected
        self.__expirationShown = False
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI
        g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        ctrl = game_control.g_instance
        ctrl.aogas.onNotifyAccount += self.__AOGAS_onNotifyAccount
        ctrl.gameSession.onClientNotify += self.__gameSession_onClientNotify
        game_control.getEventsNotificationCtrl().onEventNotificationsChanged += self.__onReceiveEventNotification

    def destroy(self):
        connectionManager.onConnected -= self.__onConnected
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        ctrl = game_control.g_instance
        ctrl.aogas.onNotifyAccount -= self.__AOGAS_onNotifyAccount
        ctrl.gameSession.onClientNotify -= self.__gameSession_onClientNotify
        game_control.getEventsNotificationCtrl().onEventNotificationsChanged += self.__onReceiveEventNotification
        self.__clearLobbyListeners()

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def pushMessage(self, text, type = SM_TYPE.Information, priority = None):
        if GUI_SETTINGS.isGuiEnabled():
            self.proto.serviceChannel.pushClientSysMessage(text, type, priority=priority)
        else:
            LOG_DEBUG('[SYSTEM MESSAGE]', text, type)

    def pushI18nMessage(self, key, *args, **kwargs):
        text = i18n.makeString(key, *args, **kwargs)
        msgType = kwargs.get('type', SM_TYPE.Information)
        msgPriority = kwargs.get('priority', None)
        self.pushMessage(text, msgType, msgPriority)
        return

    def __onAccountShowGUI(self, ctx):
        self.__checkPremiumAccountExpiry()
        for message in g_critMemHandler.messages:
            self.__onMemoryCritical(message)

        onMemCrit = getattr(g_critMemHandler, 'onMemCrit', None)
        if onMemCrit is not None:
            onMemCrit += self.__onMemoryCritical
        else:
            LOG_ERROR('MemoryCriticalController.onMemCrit is not defined')
        return

    def __onAvatarBecomePlayer(self):
        self.__clearLobbyListeners()

    def __clearLobbyListeners(self):
        onMemCrit = getattr(g_critMemHandler, 'onMemCrit', None)
        if onMemCrit is not None:
            onMemCrit -= self.__onMemoryCritical
        return

    def __onConnected(self):
        self.pushI18nMessage('#system_messages:connected', connectionManager.serverUserName, type=SM_TYPE.GameGreeting)

    def __checkPremiumAccountExpiry(self, ctx = None):
        expiryUTCTime = g_itemsCache.items.stats.premiumExpiryTime
        delta = account_helpers.getPremiumExpiryDelta(expiryUTCTime)
        if delta.days == 0 and expiryUTCTime and not self.__expirationShown:
            self.proto.serviceChannel.pushClientMessage(expiryUTCTime, SCH_CLIENT_MSG_TYPE.PREMIUM_ACCOUNT_EXPIRY_MSG)
            self.__expirationShown = True

    def __onMemoryCritical(self, message):
        msgType, key = message
        self.pushI18nMessage('#system_messages:memory_critical/%s' % key, type=SM_TYPE.Error if msgType == 1 else SM_TYPE.Warning)

    def __AOGAS_onNotifyAccount(self, message):
        self.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.AOGAS_NOTIFY_TYPE, isAlert=True, auxData=['AOGAS', message.timeout])

    def __gameSession_onClientNotify(self, sessionDuration, timeTillMidnight, playTimeLeft):
        LOG_DEBUG('onGameSessionNotification', sessionDuration, timeTillMidnight, playTimeLeft)
        if constants.IS_KOREA:
            key = '#system_messages:gameSessionControl/korea/{0:>s}'
            msgList = [i18n.makeString(key.format('sessionTime'), sessionTime=time.strftime('%H:%M', time.gmtime(sessionDuration)))]
            if not game_control.g_instance.gameSession.isAdult and timeTillMidnight <= KOREA_TIME_TILL_MIDNIGHT:
                msgList.append(i18n.makeString(key.format('timeTillMidnight'), timeLeft=time.strftime('%H:%M', time.gmtime(timeTillMidnight))))
            if playTimeLeft is not None:
                msgList.append(i18n.makeString(key.format('playTimeLeft'), timeLeft=time.strftime('%H:%M', time.gmtime(playTimeLeft))))
            msgList.append(i18n.makeString(key.format('note')))
            self.proto.serviceChannel.pushClientSysMessage('\n'.join(msgList), SM_TYPE.Warning)
        return

    def __onReceiveEventNotification(self, added, removed):
        self.__processNotifications(added, 'Begin')
        self.__processNotifications(removed, 'End')

    def __processNotifications(self, notifications, state):
        for notification in notifications:
            msgType = notification.eventType
            text = notification.text
            if msgType is not None and not msgType.startswith(self.__CMD_BLOCK_PREFIX) and not msgType.startswith(self.__PROMO_BLOCK_PREFIX) and text:
                message = {'data': text,
                 'type': msgType,
                 'state': state}
                self.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.ACTION_NOTIFY_TYPE)

        return
