# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/SystemMessagesInterface.py
# Compiled at: 2011-07-29 13:15:51
import account_helpers
from ConnectionManager import connectionManager
from helpers import i18n
from gui.AOGAS import g_controller
from gui.SystemMessages import SM_TYPE, BaseSystemMessages
from gui.Scaleform.utils.requesters import StatsRequester
from messenger import SCH_CLIENT_MSG_TYPE
from messenger.gui import MessengerDispatcher
from PlayerEvents import g_playerEvents
from MemoryCriticalController import g_critMemHandler
import weakref
from adisp import process

class SystemMessagesInterface(BaseSystemMessages):
    __dispatcher = None

    def init(self):
        self.__dispatcher = weakref.proxy(MessengerDispatcher.g_instance.serviceChannel)
        connectionManager.onConnected += self.__onConnected
        self.__expirationShown = False
        g_playerEvents.onAccountShowGUI += self.__checkPremiumAccountExpiry
        for message in g_critMemHandler.messages:
            self.__onMemoryCritical(message)

        g_critMemHandler.onMemCrit += self.__onMemoryCritical
        g_controller.onNotifyAccount += self.__AOGAS_onNotifyAccount

    def destroy(self):
        self.__dispatcher = None
        connectionManager.onConnected -= self.__onConnected
        g_playerEvents.onAccountShowGUI -= self.__checkPremiumAccountExpiry
        g_critMemHandler.onMemCrit -= self.__onMemoryCritical
        g_controller.onNotifyAccount -= self.__AOGAS_onNotifyAccount
        return

    def pushMessage(self, text, type=SM_TYPE.Information):
        self.__dispatcher.pushClientSysMessage(text, type)

    def pushI18nMessage(self, key, *args, **kwargs):
        text = i18n.makeString(key, *args, **kwargs)
        type = kwargs.get('type', SM_TYPE.Information)
        self.pushMessage(text, type)

    def __onConnected(self):
        self.pushI18nMessage('#system_messages:connected', connectionManager.serverUserName, type=SM_TYPE.GameGreeting)

    @process
    def __checkPremiumAccountExpiry(self, ctx={}):
        expiryUTCTime = yield StatsRequester().getPremiumExpiryTime()
        delta = account_helpers.getPremiumExpiryDelta(expiryUTCTime)
        if delta.days == 0 and expiryUTCTime and not self.__expirationShown:
            self.__dispatcher.pushClientMessage(expiryUTCTime, SCH_CLIENT_MSG_TYPE.PREMIUM_ACCOUNT_EXPIRY_MSG)
            self.__expirationShown = True

    def __onMemoryCritical(self, message):
        type, key = message
        self.pushI18nMessage('#system_messages:memory_critical/%s' % key, type=SM_TYPE.Error if type == 1 else SM_TYPE.Warning)

    def __AOGAS_onNotifyAccount(self, message):
        self.__dispatcher.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.AOGAS_NOTIFY_TYPE, isPriority=True, auxData=['AOGAS', message.timeout])
