# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PremiumForm.py
import BigWorld
from adisp import process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.PremiumFormMeta import PremiumFormMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.framework.entities.View import View
from gui.shared import EVENT_BUS_SCOPE, g_itemsCache
from gui.shared.events import LobbySimpleEvent
from gui.shared.utils.requesters import StatsRequester, StatsRequesterr
import account_helpers
from gui import SystemMessages, DialogsInterface
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework import AppRef
from gui.shared.utils.gui_items import formatPrice

class PremiumForm(View, AbstractWindowView, PremiumFormMeta, AppRef):

    def _populate(self):
        super(PremiumForm, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.gold': self.onSetGoldHndlr,
         'cache.mayConsumeWalletResources': self.onSetGoldHndlr})
        g_itemsCache.onSyncCompleted += self.__premiumDataRequest

    def _dispose(self):
        g_itemsCache.onSyncCompleted -= self.__premiumDataRequest
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(PremiumForm, self)._dispose()

    def onWindowClose(self):
        self.destroy()

    def onPremiumDataRequest(self):
        self.__premiumDataRequest()

    def onPremiumBuy(self, days, price):
        self.__premiumBuyRequest(days, price)

    def onSetGoldHndlr(self, _):
        self.as_setGoldS(g_itemsCache.items.stats.gold)

    @process
    def __premiumBuyRequest(self, days, price):
        stats = yield StatsRequesterr().request()
        if account_helpers.isPremiumAccount(stats.attributes):
            dialogId = 'premiumContinueConfirmation'
        else:
            dialogId = 'premiumBuyConfirmation'
        isOk = yield DialogsInterface.showDialog(I18nConfirmDialogMeta(dialogId, messageCtx={'days': int(days),
         'gold': BigWorld.wg_getGoldFormat(price)}))
        if isOk and days:
            if stats.gold < price:
                self.__systemErrorMessage(SYSTEM_MESSAGES.PREMIUM_NOT_ENOUGH_GOLD, days, SystemMessages.SM_TYPE.Warning)
            else:
                self.__upgradeToPremium(days)
            self.destroy()

    def __premiumDataRequest(self, *args):
        stats = g_itemsCache.items.stats
        premiumCost = g_itemsCache.items.shop.premiumCost
        premiumCost = sorted(premiumCost.items(), reverse=True)
        defaultPremiumCost = g_itemsCache.items.shop.defaults.premiumCost
        defaultPremiumCost = sorted(defaultPremiumCost.items(), reverse=True)
        args = []
        for idx, (period, cost) in enumerate(premiumCost):
            _, defaultCost = defaultPremiumCost[idx]
            args.append({'days': period,
             'price': defaultCost,
             'discountPrice': cost})

        gold = stats.gold
        isPremiumAccount = account_helpers.isPremiumAccount(stats.attributes)
        self.as_setCostsS(args)
        self.as_setPremiumS(isPremiumAccount)
        self.as_setGoldS(gold)

    @process
    def __upgradeToPremium(self, days):
        Waiting.show('loadStats')
        attrs = yield StatsRequester().getAccountAttrs()
        isPremium = account_helpers.isPremiumAccount(attrs)
        success = yield StatsRequester().upgradeToPremium(days)
        if success:
            premiumCost = yield StatsRequester().getPremiumCost()
            if premiumCost:
                if isPremium:
                    successMessage = SYSTEM_MESSAGES.PREMIUM_CONTINUESUCCESS
                else:
                    successMessage = SYSTEM_MESSAGES.PREMIUM_BUYINGSUCCESS
                SystemMessages.pushI18nMessage(successMessage, days, formatPrice((0, premiumCost[int(days)])), type=SystemMessages.SM_TYPE.PurchaseForGold)
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.UPDATE_TANK_PARAMS), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.__systemErrorMessage(SYSTEM_MESSAGES.PREMIUM_SERVER_ERROR, days, SystemMessages.SM_TYPE.Error)
        Waiting.hide('loadStats')

    def __systemErrorMessage(self, systemMessage, days, typeMessage):
        SystemMessages.g_instance.pushI18nMessage(systemMessage, days, type=typeMessage)
