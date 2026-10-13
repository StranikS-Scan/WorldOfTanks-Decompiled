# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wallet.py
from __future__ import absolute_import
import logging
import BigWorld
import Event
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.money import Currency
from gui.SystemMessages import SM_TYPE
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class WalletController(IWalletController):
    itemsCache = dependency.descriptor(IItemsCache)

    class STATUS(CONST_CONTAINER):
        SYNCING = 0
        NOT_AVAILABLE = 1
        AVAILABLE = 2

    def __init__(self):
        super(WalletController, self).__init__()
        self.onWalletStatusChanged = Event.Event()
        self.__currentStatus = None
        self.__currentCallbackId = None
        return

    def init(self):
        _logger.debug('WalletController init')
        g_clientUpdateManager.addCallbacks({'cache.isResourcesConsumptionAllowed': self.__onWalletStatusChanged})

    def fini(self):
        _logger.debug('WalletController fini')
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__clearCallback()
        super(WalletController, self).fini()

    def onLobbyStarted(self, ctx):
        if self.itemsCache.items.stats.isResourcesConsumptionAllowed:
            status = self.STATUS.AVAILABLE
        else:
            status = self.STATUS.SYNCING
        self.__processStatus(status, True)

    @property
    def status(self):
        return self.__currentStatus

    @property
    def componentsStatuses(self):
        return {currency:self.__currentStatus for currency in Currency.GUI_ALL + ('freeXP',)}

    @property
    def isSyncing(self):
        return self.__checkStatus(self.STATUS.SYNCING)

    @property
    def isNotAvailable(self):
        return self.__checkStatus(self.STATUS.NOT_AVAILABLE)

    @property
    def isAvailable(self):
        return self.__checkStatus(self.STATUS.AVAILABLE)

    def __processCallback(self):
        self.__currentCallbackId = None
        if self.isSyncing:
            self.__processStatus(self.STATUS.NOT_AVAILABLE)
            self.__sendNotification(status='not_available')
        return

    def __clearCallback(self):
        if self.__currentCallbackId is not None:
            BigWorld.cancelCallback(self.__currentCallbackId)
            self.__currentCallbackId = None
        return

    def __processStatus(self, status, initialize=False):
        if self.__currentStatus != status:
            self.__currentStatus = status
            self.__notify()
            _logger.info('Wallet status changed: %s(%s)', self.STATUS.getKeyByValue(self.__currentStatus), self.__currentStatus)
            if self.isAvailable:
                self.__clearCallback()
                if not initialize:
                    self.__sendNotification(status='available')
            elif self.isSyncing and self.__currentCallbackId is None:
                self.__currentCallbackId = BigWorld.callback(30, self.__processCallback)
        return

    def __onWalletStatusChanged(self, available):
        status = self.__currentStatus
        if available and not self.isAvailable:
            status = self.STATUS.AVAILABLE
        elif not available and self.isAvailable:
            status = self.STATUS.SYNCING
        self.__processStatus(status)

    def __checkStatus(self, status):
        return self.__currentStatus == status

    def __notify(self):
        self.onWalletStatusChanged(self.status)

    def __sendNotification(self, status):
        msgType = SM_TYPE.Information if status == 'available' else SM_TYPE.Warning
        SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.getWalletStatus(status), type=msgType)
