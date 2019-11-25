# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/anonymizer_controller.py
import logging
import BigWorld
from Event import Event
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.anonymizer.contacts_uploader import ContactsUploader
from helpers import dependency
from skeletons.gui.game_control import IAnonymizerController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_RSettingsError = R.strings.messenger.server.errors.settingError

class AnonymizerController(IAnonymizerController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__isEnabled', '__isRestricted', '__isAnonymized', '__isInBattle', '__uploader')

    def __init__(self):
        self.onStateChanged = Event()
        self.__isEnabled = False
        self.__isRestricted = False
        self.__isAnonymized = False
        self.__isInBattle = False
        self.__uploader = ContactsUploader()

    def onConnected(self):
        self.__uploader.init()

    def onDisconnected(self):
        self.__uploader.fini()
        self.__clear()

    def onLobbyInited(self, _):
        self.__isInBattle = False
        self.__addListeners()
        self.__update()

    def onAvatarBecomePlayer(self):
        self.__removeListeners()
        self.__isInBattle = True

    def onAccountBecomeNonPlayer(self):
        if self.__uploader.isProcessing:
            _logger.info('contacts uploader stopping because of onAccountBecomeNonPlayer.')
            self.__uploader.stop()

    @property
    def isInBattle(self):
        return self.__isInBattle

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def isRestricted(self):
        return self.__isRestricted

    @property
    def isAnonymized(self):
        return self.__isEnabled and self.__isAnonymized

    def setAnonymized(self, value):
        if self.isEnabled and not self.isRestricted:
            if value != self.__isAnonymized:
                self.__isAnonymized = value
                BigWorld.player().anonymizer.setAnonymized(self.__isAnonymized, self.__onSetAnonymizedResponse)
        else:
            self.__pushChangeUnavailableMessage()

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'cache.SPA': self.__onCacheSPAChanged,
         'anonymizer.enabled': self.__onAnonymizedStateChanged,
         'anonymizer.contactsFeedback': self.__onContactsFeedback})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __update(self):
        self.__isEnabled = self.__lobbyContext.getServerSettings().isAnonymizerEnabled()
        self.__isRestricted = self.__itemsCache.items.stats.isAnonymousRestricted
        self.__isAnonymized = self.__itemsCache.items.anonymizer.isPlayerAnonymized
        self.__processContacts()
        self.onStateChanged(enabled=self.isEnabled, restricted=self.isRestricted, anonymized=self.isAnonymized)

    def __clear(self):
        self.onStateChanged.clear()
        self.__removeListeners()
        self.__isEnabled = False
        self.__isRestricted = False
        self.__isAnonymized = False
        self.__isInBattle = False

    def __onServerSettingsChanged(self, *_):
        self.__isEnabled = self.__lobbyContext.getServerSettings().isAnonymizerEnabled()
        self.onStateChanged(enabled=self.isEnabled)

    def __onCacheSPAChanged(self, *_):
        self.__isRestricted = self.__itemsCache.items.stats.isAnonymousRestricted
        self.onStateChanged(restricted=self.isRestricted)

    def __onAnonymizedStateChanged(self, *_):
        self.__isAnonymized = self.__itemsCache.items.anonymizer.isPlayerAnonymized
        self.onStateChanged(anonymized=self.isAnonymized)

    def __onContactsFeedback(self, *_):
        self.__processContacts()

    def __processContacts(self):
        contactsFeedback = self.__itemsCache.items.anonymizer.contactsFeedback
        if contactsFeedback:
            arenaUniqueID, contactsBlob = self.__itemsCache.items.anonymizer.contactsFeedback[0]
            if self.__uploader.isProcessing:
                if self.__uploader.arenaUniqueID == arenaUniqueID:
                    _logger.info('contacts uploader continue upload arenaID %s', arenaUniqueID)
                    return
                self.__uploader.stop()
            self.__uploader.start(arenaUniqueID, contactsBlob)
        elif self.__uploader.isProcessing:
            self.__uploader.stop()

    def __onSetAnonymizedResponse(self, resultID, errorCode):
        if errorCode:
            self.__onAnonymizedStateChanged()
            self.__pushChangeUnavailableMessage()
        _logger.debug('setAnonymized response: %s', (resultID, errorCode))

    @staticmethod
    def __pushChangeUnavailableMessage():
        SystemMessages.pushMessage(backport.text(_RSettingsError.changeUnavailable.message()), SystemMessages.SM_TYPE.Warning)
