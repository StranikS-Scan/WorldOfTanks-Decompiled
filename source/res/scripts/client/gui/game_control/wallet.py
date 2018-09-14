# Embedded file name: scripts/client/gui/game_control/wallet.py
import BigWorld
from adisp import process
import Event
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.FreeXPInfoDialogMeta import FreeXPInfoMeta
from gui.SystemMessages import SM_TYPE
from gui.game_control.controllers import Controller
from gui.shared import g_itemsCache
from shared_utils import CONST_CONTAINER
from helpers.aop import Aspect, Pointcut, Weaver

class WalletController(Controller):

    class STATUS(CONST_CONTAINER):
        SYNCING = 0
        NOT_AVAILABLE = 1
        AVAILABLE = 2

    def __init__(self, proxy):
        super(WalletController, self).__init__(proxy)
        self.onWalletStatusChanged = Event.Event()
        self.__currentStatus = None
        self.__currentCallbackId = None
        self.__useGold = False
        self.__useFreeXP = False
        self.__weaver = None
        return

    def init(self):
        g_clientUpdateManager.addCallbacks({'cache.mayConsumeWalletResources': self.__onWalletStatusChanged})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__clearCallback()
        self.__clearWeaver()
        super(WalletController, self).fini()

    def onLobbyStarted(self, ctx):
        wallet = BigWorld.player().serverSettings['wallet']
        self.__useGold = bool(wallet[0])
        self.__useFreeXP = bool(wallet[1])
        if self.__useFreeXP:
            self.__checkFreeXPConditions()
        self.__processStatus(self.STATUS.AVAILABLE if g_itemsCache.items.stats.mayConsumeWalletResources else self.STATUS.SYNCING, True)

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
         'freeXP': self.__currentStatus if self.__useFreeXP else self.STATUS.AVAILABLE}

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

    def cleanWeave(self, obj):
        if self.__weaver:
            for value in obj:
                self.__weaver.clear(idx=self.__weaver.findPointcut(value))

    def __clearWeaver(self):
        if self.__weaver is not None:
            self.__weaver.clear()
            self.__weaver = None
        return

    def __processCallback(self):
        self.__currentCallbackId = None
        if self.isSyncing:
            self.__processStatus(self.STATUS.NOT_AVAILABLE)
            message = '#system_messages:wallet/not_available'
            if not self.__useFreeXP:
                message += '_gold'
            elif not self.__useGold:
                message += '_freexp'
            SystemMessages.g_instance.pushI18nMessage(message, type=SM_TYPE.Warning)
        return

    def __clearCallback(self):
        if self.__currentCallbackId is not None:
            BigWorld.cancelCallback(self.__currentCallbackId)
            self.__currentCallbackId = None
        return

    def __processStatus(self, status, initialize = False):
        if self.__currentStatus != status:
            self.__currentStatus = status
            self.__notify()
            LOG_DEBUG('Wallet status changed:', self.__currentStatus)
            if self.isAvailable:
                self.__clearCallback()
                if not initialize:
                    message = '#system_messages:wallet/available'
                    if not self.__useFreeXP:
                        message += '_gold'
                    elif not self.__useGold:
                        message += '_freexp'
                    SystemMessages.g_instance.pushI18nMessage(message, type=SM_TYPE.Information)
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
        from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = g_settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        if filters['isFreeXPInfoDialogShowed']:
            return
        self.__weaver = Weaver()
        if self.__weaver.findPointcut(ResearchViewPointcut) is -1:
            self.__weaver.weave(pointcut=ResearchViewPointcut, aspects=[ShowXPInfoDialogAspect(self.cleanWeave)])
        if self.__weaver.findPointcut(ExchangeFreeXPToTankmanPointcut) is -1:
            self.__weaver.weave(pointcut=ExchangeFreeXPToTankmanPointcut, aspects=[ShowXPInfoDialogAspect(self.cleanWeave)])


class ShowXPInfoDialogAspect(Aspect):

    def __init__(self, callBack):
        super(ShowXPInfoDialogAspect, self).__init__()
        self.callback = callBack

    @process
    def atCall(self, cd):
        from gui import DialogsInterface
        from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = g_settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        filters['isFreeXPInfoDialogShowed'] = True
        g_settingsCore.serverSettings.setSection(GUI_START_BEHAVIOR, filters)
        cd.avoid()
        yield DialogsInterface.showDialog(FreeXPInfoMeta())
        cd.function(*cd._packArgs(), **cd._kwargs)
        self.callback([ExchangeFreeXPToTankmanPointcut, ResearchViewPointcut])

    def clear(self):
        self.callback = None
        return


class ResearchViewPointcut(Pointcut):

    def __init__(self):
        super(ResearchViewPointcut, self).__init__('gui.Scaleform.daapi.view.lobby.techtree.ResearchView', 'ResearchView', '^unlockItem$')


class ExchangeFreeXPToTankmanPointcut(Pointcut):

    def __init__(self):
        super(ExchangeFreeXPToTankmanPointcut, self).__init__('gui.Scaleform.daapi.view.lobby.exchange.ExchangeFreeToTankmanXpWindow', 'ExchangeFreeToTankmanXpWindow', '^apply$')
