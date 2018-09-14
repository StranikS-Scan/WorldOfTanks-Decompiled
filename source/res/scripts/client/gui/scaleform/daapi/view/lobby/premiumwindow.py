# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PremiumWindow.py
import BigWorld
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.meta.PremiumWindowMeta import PremiumWindowMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import g_itemsCache
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items.processors.common import PremiumAccountBuyer
from gui.shared.tooltips import ACTION_TOOLTIPS_STATE, ACTION_TOOLTIPS_TYPE
from gui import makeHtmlString, game_control, SystemMessages
from gui.shared.utils.decorators import process
from helpers import i18n, time_utils
BTN_WIDTH = 120
PREMIUM_PACKET_LOCAL_KEY = '#menu:premium/packet/days%s'

class PremiumWindow(PremiumWindowMeta):

    def __init__(self, ctx = None):
        super(PremiumWindow, self).__init__()
        self._items = g_itemsCache.items
        self._actualPremiumCost = None
        if ctx is not None:
            self._arenaUniqueID = ctx.get('arenaUniqueID', 0)
        else:
            self._arenaUniqueID = 0
        return

    def onBtnClick(self, action):
        if action == 'closeAction':
            self.onWindowClose()

    def onRateClick(self, packetID):
        period = int(packetID)
        self.__premiumBuyRequest(period, self._actualPremiumCost[period])

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(PremiumWindow, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.gold': self.__onUpdateHandler,
         'stats.unlocks': self.__onUpdateHandler,
         'cache.mayConsumeWalletResources': self.__onUpdateHandler,
         'goodies': self.__onUpdateHandler})
        game_control.g_instance.gameSession.onPremiumNotify += self.__onUpdateHandler
        g_itemsCache.onSyncCompleted += self.__onUpdateHandler
        self.__populateData()

    def _dispose(self):
        g_itemsCache.onSyncCompleted -= self.__onUpdateHandler
        game_control.g_instance.gameSession.onPremiumNotify -= self.__onUpdateHandler
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._items = None
        self._actualPremiumCost = None
        super(PremiumWindow, self)._dispose()
        return

    def __onUpdateHandler(self, *args):
        premiumPackets, self._actualPremiumCost, selectedPacketID = self.__getPremiumPackets()
        self.as_setRatesS(MENU.PREMIUM_TARIFFS_HEADER, premiumPackets, selectedPacketID)
        self.as_setButtonsS(self.__getBtnData(), TEXT_ALIGN.RIGHT, BTN_WIDTH)

    @process('loadStats')
    def __premiumBuyRequest(self, days, cost):
        wasPremium = g_itemsCache.items.stats.isPremium
        arenaUniqueID = self._arenaUniqueID
        result = yield PremiumAccountBuyer(days, cost, arenaUniqueID).request()
        if not result.success and result.auxData and result.auxData.get('errStr', '') in ('Battle not in cache', 'Not supported'):
            arenaUniqueID = 0
            result = yield PremiumAccountBuyer(days, cost, arenaUniqueID, withoutBenefits=True).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            becomePremium = g_itemsCache.items.stats.isPremium and not wasPremium
            self.onWindowClose()
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.PREMIUM_BOUGHT, ctx={'arenaUniqueID': arenaUniqueID,
             'becomePremium': becomePremium}))

    def __populateData(self):
        self.as_setImageS(RES_ICONS.MAPS_ICONS_WINDOWS_PREM_PREMHEADER, 0)
        self.as_setWindowTitleS(self.__getTitle())
        self.as_setHeaderS(MENU.PREMIUM_PERCENTFACTOR, MENU.PREMIUM_BONUS1, MENU.PREMIUM_BONUS2)
        premiumPackets, self._actualPremiumCost, selectedPacketID = self.__getPremiumPackets()
        self.as_setRatesS(MENU.PREMIUM_TARIFFS_HEADER, premiumPackets, selectedPacketID)
        self.as_setButtonsS(self.__getBtnData(), TEXT_ALIGN.RIGHT, BTN_WIDTH)

    def __getTitle(self):
        if self.__isPremiumAccount():
            return MENU.PREMIUM_CONTINUEMESSAGE
        return MENU.PREMIUM_BUYMESSAGE

    def __getSubmitBtnLabel(self):
        if self.__isPremiumAccount():
            return MENU.PREMIUM_SUBMITCONTINUE
        return MENU.PREMIUM_SUBMITBUY

    def __isPremiumAccount(self):
        return self._items.stats.isPremium

    def __getPremiumPackets(self):
        premiumCost = sorted(self._items.shop.getPremiumCostWithDiscount().items(), reverse=True)
        defaultPremiumCost = sorted(self._items.shop.defaults.premiumCost.items(), reverse=True)
        packetVOs = []
        accGold = self._items.stats.gold
        canBuyPremium = self.__canBuyPremium()
        selectedPacket = 0
        actualPremiumCost = {}
        for idx, (period, cost) in enumerate(premiumCost):
            _, defaultCost = defaultPremiumCost[idx]
            packetVOs.append(self.__makePacketVO(period, cost, defaultCost, accGold, canBuyPremium))
            actualPremiumCost[period] = cost
            if accGold >= cost:
                selectedPacket = max(selectedPacket, period)

        return (packetVOs, actualPremiumCost, str(selectedPacket))

    def __makePacketVO(self, period, cost, defaultCost, accGold, canBuyPremium):
        isEnoughMoney = accGold >= cost
        action = self.__getAction(cost, defaultCost, period)
        hasAction = action is not None
        return {'id': str(period),
         'image': '../maps/icons/windows/prem/icon_prem%d_98.png' % period,
         'duration': self.__getDurationStr(period, cost, hasAction, isEnoughMoney),
         'actionPrice': action,
         'enabled': canBuyPremium and isEnoughMoney,
         'haveMoney': isEnoughMoney}

    def __getAction(self, cost, defaultCost, period):
        if cost != defaultCost:
            return {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
             'key': 'premiumPacket%dCost' % period,
             'isBuying': True,
             'state': (None, ACTION_TOOLTIPS_STATE.DISCOUNT),
             'newPrice': (0, cost),
             'oldPrice': (0, defaultCost)}
        else:
            return None

    def __canBuyPremium(self):
        if self.__isPremiumAccount():
            premiumExpiryTime = self._items.stats.premiumExpiryTime
        else:
            premiumExpiryTime = 0
        deltaInSeconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(premiumExpiryTime)))
        return deltaInSeconds < time_utils.ONE_YEAR

    def __getDurationStr(self, period, cost, hasAction, isEnoughMoney):
        priceStr = ''
        if not hasAction:
            key = 'gold' if isEnoughMoney else 'goldAlert'
            priceStr = makeHtmlString('html_templates:lobby/dialogs/premium', key, ctx={'value': BigWorld.wg_getGoldFormat(cost)})
        duration = i18n.makeString(PREMIUM_PACKET_LOCAL_KEY % period)
        ctx = {'duration': duration,
         'price': priceStr}
        return makeHtmlString('html_templates:lobby/dialogs/premium', 'duration', ctx=ctx)

    def __getBtnData(self):
        return [{'label': self.__getSubmitBtnLabel(),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_NORMAL,
          'action': 'buyAction',
          'isFocused': True,
          'tooltip': '',
          'enabled': self.__isBuyBtnEnabled(),
          'btnName': 'submitButton'}, {'label': MENU.PREMIUM_CANCEL,
          'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK,
          'action': 'closeAction',
          'isFocused': False,
          'tooltip': '',
          'btnName': 'closeButton'}]

    def __isBuyBtnEnabled(self):
        premiumCost = self._items.shop.getPremiumCostWithDiscount()
        if len(premiumCost) > 0:
            minPremiumPacketCost = min(premiumCost.values())
            return self._items.stats.gold >= minPremiumPacketCost and self.__canBuyPremium()
        return False
