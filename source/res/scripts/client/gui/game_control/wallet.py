# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wallet.py
import logging
import BigWorld
import Event
import constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from adisp import process
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.FreeXPInfoDialogMeta import FreeXPInfoMeta
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE
from helpers import dependency
from helpers.aop import Aspect, Pointcut, Weaver
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class WalletController(IWalletController):
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)

    class STATUS(CONST_CONTAINER):
        SYNCING = 0
        NOT_AVAILABLE = 1
        AVAILABLE = 2

    def __init__(self):
        super(WalletController, self).__init__()
        self.onWalletStatusChanged = Event.Event()
        self.__currentStatus = None
        self.__currentCallbackId = None
        self.__useGold = False
        self.__useFreeXP = False
        self.__weaver = None
        return

    def init(self):
        _logger.debug('WalletController init')
        g_clientUpdateManager.addCallbacks({'cache.mayConsumeWalletResources': self.__onWalletStatusChanged})

    def fini(self):
        _logger.debug('WalletController fini')
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__clearCallback()
        self.__clearWeaver()
        super(WalletController, self).fini()

    def onLobbyStarted(self, event):
        wallet = BigWorld.player().serverSettings['wallet']
        self.__useGold = bool(wallet[0])
        self.__useFreeXP = bool(wallet[1])
        if self.__useFreeXP:
            self.__checkFreeXPConditions()
        if self.itemsCache.items.stats.mayConsumeWalletResources:
            status = self.STATUS.AVAILABLE
        else:
            status = self.STATUS.SYNCING
        self.__processStatus(status, True)

    def onAvatarBecomePlayer(self):
        self.__clearWeaver()

    def onDisconnected(self):
        self.__clearWeaver()

    @property
    def status(self):
        return self.__currentStatus

    @property
    def componentsStatuses(self):
        return {'gold': self.__currentStatus if self.__useGold else self.STATUS.AVAILABLE,
         'freeXP': self.__currentStatus if self.__useFreeXP else self.STATUS.AVAILABLE,
         'credits': self.__currentStatus if not constants.IS_CHINA else self.STATUS.AVAILABLE,
         'crystal': self.__currentStatus if not constants.IS_CHINA else self.STATUS.AVAILABLE,
         'eventCoin': self.__currentStatus if not constants.IS_CHINA else self.STATUS.AVAILABLE,
         'bpcoin': self.__currentStatus if not constants.IS_CHINA else self.STATUS.NOT_AVAILABLE}

    @property
    def isSyncing(self):
        return self.__checkStatus(self.STATUS.SYNCING)

    @property
    def isNotAvailable(self):
        return self.__checkStatus(self.STATUS.NOT_AVAILABLE)

    @property
    def isAvailable(self):
        return self.__checkStatus(self.STATUS.AVAILABLE)

    @property
    def useGold(self):
        return self.__useGold

    @property
    def useFreeXP(self):
        return self.__useFreeXP

    def cleanWeave(self, pointcuts):
        if self.__weaver:
            for pointcut in pointcuts:
                self.__weaver.clear(idx=self.__weaver.findPointcut(pointcut))

    def __clearWeaver(self):
        if self.__weaver is not None:
            self.__weaver.clear()
            self.__weaver = None
        return

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
        self.onWalletStatusChanged(self.componentsStatuses)

    def __checkFreeXPConditions(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        if filters['isFreeXPInfoDialogShowed']:
            return
        self.__weaver = Weaver()
        if self.__weaver.findPointcut(UnlockItemPointcut) == -1:
            self.__weaver.weave(pointcut=UnlockItemPointcut, aspects=[ShowXPInfoDialogAspect(self.cleanWeave)])
        if self.__weaver.findPointcut(ExchangeFreeXPToTankmanPointcut) == -1:
            self.__weaver.weave(pointcut=ExchangeFreeXPToTankmanPointcut, aspects=[ShowXPInfoDialogAspect(self.cleanWeave)])

    def __sendNotification(self, status):
        msgType = SM_TYPE.Information if status == 'available' else SM_TYPE.Warning
        if constants.IS_CHINA:
            if not self.__useFreeXP:
                status += '_gold'
            elif not self.__useGold:
                status += '_freexp'
        SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.getWalletStatus(status), type=msgType)


class ShowXPInfoDialogAspect(Aspect):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, callBack):
        super(ShowXPInfoDialogAspect, self).__init__()
        self.callback = callBack

    @process
    def atCall(self, cd):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        filters['isFreeXPInfoDialogShowed'] = True
        self.settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)
        cd.avoid()
        yield DialogsInterface.showDialog(FreeXPInfoMeta())
        cd.function(*cd._packArgs(), **cd._kwargs)
        self.callback((ExchangeFreeXPToTankmanPointcut, UnlockItemPointcut))

    def clear(self):
        self.callback = None
        return


class UnlockItemPointcut(Pointcut):

    def __init__(self):
        super(UnlockItemPointcut, self).__init__('gui.shared.gui_items.items_actions.actions', 'UnlockItemAction', '^_unlockItem$')


class ExchangeFreeXPToTankmanPointcut(Pointcut):

    def __init__(self):
        super(ExchangeFreeXPToTankmanPointcut, self).__init__('gui.Scaleform.daapi.view.lobby.exchange.ExchangeFreeToTankmanXpWindow', 'ExchangeFreeToTankmanXpWindow', '^apply$')
