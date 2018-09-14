# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PremiumWindow.py
import BigWorld
from gui import makeHtmlString, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.meta.PremiumWindowMeta import PremiumWindowMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import g_itemsCache
from gui.shared.events import LobbySimpleEvent
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.processors.common import PremiumAccountBuyer
from gui.shared.money import Money
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.decorators import process
from helpers import i18n, time_utils, dependency
from skeletons.gui.game_control import IGameSessionController
BTN_WIDTH = 120
PREMIUM_PACKET_LOCAL_KEY = '#menu:premium/packet/days%s'

class PremiumWindow(PremiumWindowMeta):
    gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self, ctx=None):
        super(PremiumWindow, self).__init__()
        self._items = g_itemsCache.items
        self._actualPremiumCost = None
        self._arenaUniqueID = 0
        self._premiumBonusesDiff = None
        if ctx is not None:
            self._arenaUniqueID = ctx.get('arenaUniqueID', 0)
            self._premiumBonusesDiff = ctx.get('premiumBonusesDiff', None)
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
        self.gameSession.onPremiumNotify += self.__onUpdateHandler
        g_itemsCache.onSyncCompleted += self.__onUpdateHandler
        self.__populateData()

    def _dispose(self):
        g_itemsCache.onSyncCompleted -= self.__onUpdateHandler
        self.gameSession.onPremiumNotify -= self.__onUpdateHandler
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._items = None
        self._actualPremiumCost = None
        super(PremiumWindow, self)._dispose()
        return

    def __onUpdateHandler(self, *args):
        self.__updateData()

    def __canUpdatePremium(self):
        if self.__isPremiumAccount():
            deltaInSeconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self._items.stats.premiumExpiryTime)))
            return deltaInSeconds < time_utils.ONE_YEAR
        return True

    def __updateData(self):
        canUpdatePremium = self.__canUpdatePremium()
        premiumPackets, self._actualPremiumCost, selectedPacketID = self.__getPremiumPackets(canUpdatePremium)
        cantUpgradeTooltip = '' if canUpdatePremium else formatters.getLimitExceededPremiumTooltip()
        self.__setRates(self.__getHeaderText(canUpdatePremium), cantUpgradeTooltip, premiumPackets, selectedPacketID)
        self.as_setButtonsS(self.__getBtnData(cantUpgradeTooltip), TEXT_ALIGN.RIGHT, BTN_WIDTH)

    def __setRates(self, header, headerTooltip, premiumPackets, selectedPacketID):
        self.as_setRatesS({'header': header,
         'headerTooltip': headerTooltip,
         'rates': premiumPackets,
         'selectedRateId': selectedPacketID})

    @process('loadStats')
    def __premiumBuyRequest(self, days, cost):
        wasPremium = g_itemsCache.items.stats.isPremium
        arenaUniqueID = self._arenaUniqueID
        result = yield PremiumAccountBuyer(days, cost, arenaUniqueID).request()
        if not result.success and result.auxData and result.auxData.get('errStr', '') in ('Battle not in cache', 'Not supported'):
            arenaUniqueID = 0
            result = yield PremiumAccountBuyer(days, cost, arenaUniqueID, withoutBenefits=True).request()
        if len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            if arenaUniqueID and self._premiumBonusesDiff:
                SystemMessages.pushI18nMessage('#system_messages:premium/post_battle_premium', type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM, **self._premiumBonusesDiff)
            becomePremium = g_itemsCache.items.stats.isPremium and not wasPremium
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.PREMIUM_BOUGHT, ctx={'arenaUniqueID': arenaUniqueID,
             'becomePremium': becomePremium}))
            self.onWindowClose()

    def __populateData(self):
        self.as_setImageS(RES_ICONS.MAPS_ICONS_WINDOWS_PREM_PREMHEADER, 0)
        self.as_setWindowTitleS(self.__getTitle())
        self.as_setHeaderS(MENU.PREMIUM_PERCENTFACTOR, MENU.PREMIUM_BONUS1, MENU.PREMIUM_BONUS2)
        self.__updateData()

    def __getTitle(self):
        return MENU.PREMIUM_CONTINUEMESSAGE if self.__isPremiumAccount() else MENU.PREMIUM_BUYMESSAGE

    def __getSubmitBtnLabel(self):
        return MENU.PREMIUM_SUBMITCONTINUE if self.__isPremiumAccount() else MENU.PREMIUM_SUBMITBUY

    def __isPremiumAccount(self):
        return self._items.stats.isPremium

    def __getPremiumPackets(self, canUpdatePremium):
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
            if canUpdatePremium and accGold >= cost:
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
        return packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'premiumPacket%dCost' % period, True, Money(gold=cost), Money(gold=defaultCost)) if cost != defaultCost else None

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

    def __getHeaderText(self, canUpdatePremium):
        text = text_styles.highTitle(MENU.PREMIUM_TARIFFS_HEADER)
        if not canUpdatePremium:
            text += ' ' + icons.alert()
        return text

    def __getBtnData(self, submitBtnTooltip):
        return [{'label': self.__getSubmitBtnLabel(),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_NORMAL,
          'action': 'buyAction',
          'isFocused': True,
          'tooltip': submitBtnTooltip,
          'enabled': self.__isBuyBtnEnabled(),
          'mouseEnabledOnDisabled': True,
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
