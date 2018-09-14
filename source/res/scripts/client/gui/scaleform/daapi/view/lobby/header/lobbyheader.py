# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/LobbyHeader.py
import math
import BigWorld
from CurrentVehicle import g_currentVehicle
import account_helpers
from adisp import process
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, REQUEST_TYPE
from helpers import i18n, time_utils
from debug_utils import LOG_ERROR
from gui import makeHtmlString, game_control
from gui.LobbyContext import g_lobbyContext
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.context import PrebattleAction
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import events
from gui.shared import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils import CONST_CONTAINER
from gui.shared.ClanCache import g_clanCache
from gui.server_events import g_eventsCache
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LobbyHeaderMeta import LobbyHeaderMeta
from gui.Scaleform.framework import g_entitiesFactories, ViewTypes, AppRef
from ConnectionManager import connectionManager
_MAX_HEADER_SERVER_NAME_LEN = 6
_SERVER_NAME_PREFIX = '%s..'

class LobbyHeader(LobbyHeaderMeta, AppRef, GlobalListener):

    class BUTTONS(CONST_CONTAINER):
        SETTINGS = 'settings'
        ACCOUNT = 'account'
        PREM = 'prem'
        SQUAD = 'squad'
        GOLD = 'gold'
        SILVER = 'silver'
        FREE_XP = 'freeXP'
        BATTLE_SELECTOR = 'battleSelector'

    def _populate(self):
        battle_selector_items.create()
        super(LobbyHeader, self)._populate()
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        game_control.g_instance.wallet.onWalletStatusChanged += self.__onWalletChanged
        game_control.g_instance.gameSession.onPremiumNotify += self.__onPremiumTimeChanged
        g_currentVehicle.onChanged += self.__onVehicleChanged
        g_eventsCache.onSyncCompleted += self.__onEventsCacheResync
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.BubbleTooltipEvent.SHOW, self.__showBubbleTooltip, scope=EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__setCredits,
         'stats.gold': self.__setGold,
         'stats.freeXP': self.__setFreeXP,
         'stats.clanInfo': self.__setClanInfo,
         'account.premiumExpiryTime': self.__onPremiumExpireTimeChanged})
        self.as_setFightButtonS(i18n.makeString('#menu:headerButtons/battle'))
        self.as_setWalletStatusS(game_control.g_instance.wallet.componentsStatuses)
        self.updateAccountInfo()
        self.startGlobalListening()
        self.__updateServerName()
        Waiting.hide('enter')

    def __updateServerName(self):
        serverShortName = connectionManager.serverUserNameShort.split()[-1].strip()
        if len(serverShortName) > _MAX_HEADER_SERVER_NAME_LEN:
            serverShortName = _SERVER_NAME_PREFIX % serverShortName[:_MAX_HEADER_SERVER_NAME_LEN]
        self.as_setServerS(serverShortName)

    def _dispose(self):
        battle_selector_items.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.BubbleTooltipEvent.SHOW, self.__showBubbleTooltip, scope=EVENT_BUS_SCOPE.LOBBY)
        game_control.g_instance.gameSession.onPremiumNotify -= self.__onPremiumTimeChanged
        game_control.g_instance.wallet.onWalletStatusChanged -= self.__onWalletChanged
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheResync
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.stopGlobalListening()
        super(LobbyHeader, self)._dispose()

    def onPreQueueSettingsChanged(self, _):
        self.__updatePrebattleControls()

    def updateAccountInfo(self):
        self.updateMoneyStats()
        self.updateXPInfo()
        self.updateClanInfo()
        self.updateAccountAttrs()

    def updateMoneyStats(self):
        actualCredits, actualGold = g_itemsCache.items.stats.actualMoney
        self.__setCredits(actualCredits)
        self.__setGold(actualGold)

    def updateXPInfo(self):
        self.__setFreeXP(g_itemsCache.items.stats.actualFreeXP)

    def updateClanInfo(self):
        self.__setClanInfo(g_clanCache.clanInfo)

    def updateAccountAttrs(self):
        stats = g_itemsCache.items.stats
        accAttrs = stats.attributes
        isPremium = account_helpers.isPremiumAccount(accAttrs)
        if isPremium:
            premiumExpiryTime = stats.premiumExpiryTime
        else:
            premiumExpiryTime = 0
        battle_selector_items.getItems().validateAccountAttrs(accAttrs)
        self.__setAccountsAttrs(isPremium, premiumExpiryTime=premiumExpiryTime)

    def onPayment(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.PAYMENT))

    def showLobbyMenu(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def menuItemClick(self, alias):
        self.__triggerViewLoad(alias)

    def showExchangeWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def showExchangeXPWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EXCHANGE_XP_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def showPremiumDialog(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PREMIUM_DIALOG))

    def fightClick(self, mapID, actionName):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.doAction(PrebattleAction(actionName, mapID=mapID))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    def showSquad(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.doSelectAction(PrebattleAction(PREBATTLE_ACTION_NAME.SQUAD))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    @process
    def __setClanInfo(self, clanInfo):
        yield lambda callback: callback(True)
        name = BigWorld.player().name
        if clanInfo and len(clanInfo) > 1:
            clanAbbrev = clanInfo[1]
        else:
            clanAbbrev = None
        self.as_nameResponseS(g_lobbyContext.getPlayerFullName(name, clanInfo=clanInfo), name, clanAbbrev, g_itemsCache.items.stats.isTeamKiller, clanInfo is not None)
        clanEmblem = yield g_clanCache.getClanEmblemID()
        if clanEmblem is not None:
            self.as_setClanEmblemS(clanEmblem)
        return

    def __onPremiumExpireTimeChanged(self, timestamp):
        self.updateAccountAttrs()

    def __setCredits(self, accCredits):
        self.as_creditsResponseS(BigWorld.wg_getIntegralFormat(accCredits))

    def __setGold(self, gold):
        self.as_goldResponseS(BigWorld.wg_getGoldFormat(gold))

    def __setFreeXP(self, freeXP):
        self.as_setFreeXPS(BigWorld.wg_getIntegralFormat(freeXP), game_control.g_instance.wallet.useFreeXP)

    def __setAccountsAttrs(self, isPremiumAccount, premiumExpiryTime = 0):
        disableTTHeader = ''
        disableTTBody = ''
        if isPremiumAccount:
            if not premiumExpiryTime > 0:
                raise AssertionError
                deltaInSeconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(premiumExpiryTime)))
                if deltaInSeconds > time_utils.ONE_DAY:
                    timeLeft = math.ceil(deltaInSeconds / time_utils.ONE_DAY)
                    timeMetric = i18n.makeString('#menu:header/account/premium/days')
                else:
                    timeLeft = math.ceil(deltaInSeconds / time_utils.ONE_HOUR)
                    timeMetric = i18n.makeString('#menu:header/account/premium/hours')
                buyPremiumLabel = i18n.makeString('#menu:headerButtons/doLabel/premium')
                premiumBtnLbl = makeHtmlString('html_templates:lobby/header', 'premium-account-label', {'timeMetric': timeMetric,
                 'timeLeft': timeLeft})
                canUpdatePremium = deltaInSeconds < time_utils.ONE_YEAR
            else:
                canUpdatePremium = True
                premiumBtnLbl = makeHtmlString('html_templates:lobby/header', 'base-account-label')
                buyPremiumLabel = i18n.makeString('#menu:common/premiumBuy')
            disableTTHeader = canUpdatePremium or i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_HEADER)
            disableTTBody = i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_BODY, number=time_utils.ONE_YEAR / time_utils.ONE_DAY)
        self.as_doDisableHeaderButtonS(self.BUTTONS.PREM, canUpdatePremium)
        self.as_setPremiumParamsS(isPremiumAccount, premiumBtnLbl, buyPremiumLabel, canUpdatePremium, disableTTHeader, disableTTBody)

    def __triggerViewLoad(self, alias):
        if alias == 'browser':
            game_control.getChinaCtrl().showBrowser()
        else:
            event = g_entitiesFactories.makeLoadEvent(alias)
            if event is not None:
                self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
            else:
                LOG_ERROR('Invalid subview alias', alias)
                return
        self.as_setScreenS(alias)
        return

    def __onWalletChanged(self, status):
        self.as_goldResponseS(BigWorld.wg_getGoldFormat(g_itemsCache.items.stats.actualGold))
        self.as_setFreeXPS(BigWorld.wg_getIntegralFormat(g_itemsCache.items.stats.actualFreeXP), game_control.g_instance.wallet.useFreeXP)
        self.as_setWalletStatusS(status)

    def __onPremiumTimeChanged(self, isPremium, _, premiumExpiryTime):
        self.__setAccountsAttrs(isPremium, premiumExpiryTime=premiumExpiryTime)

    def __onViewAddedToContainer(self, _, pyEntity):
        settings = pyEntity.settings
        if settings.type is ViewTypes.LOBBY_SUB:
            if settings.alias == VIEW_ALIAS.BATTLE_QUEUE:
                self.as_doDisableNavigationS()
            else:
                self.as_setScreenS(settings.alias)

    def __getBattleTypeSelectPopover(self):
        container = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        view = None
        if container:
            view = container.getView({POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER})
        return view

    def __closeBattleTypeSelectPopover(self):
        view = self.__getBattleTypeSelectPopover()
        if view:
            view.destroy()

    def __updateBattleTypeSelectPopover(self):
        view = self.__getBattleTypeSelectPopover()
        if view:
            view.update()

    def __updatePrebattleControls(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if not prbDispatcher:
            return
        items = battle_selector_items.getItems()
        state = prbDispatcher.getFunctionalState()
        selected = items.update(state)
        canDo, _ = prbDispatcher.canPlayerDoAction()
        playerInfo = prbDispatcher.getPlayerInfo()
        if selected.isInSquad(state):
            self.as_updateSquadS(True)
        else:
            self.as_doDisableHeaderButtonS(self.BUTTONS.SQUAD, not state.hasLockedState)
            self.as_updateSquadS(False)
        self.as_disableFightButtonS(not canDo or selected.isFightButtonForcedDisabled(), '')
        self.as_setFightButtonS(selected.getFightButtonLabel(state, playerInfo))
        self.as_updateBattleTypeS(i18n.makeString(selected.getLabel()), selected.getSmallIcon(), not selected.isDisabled())
        if selected.isDisabled():
            self.__closeBattleTypeSelectPopover()
        else:
            self.__updateBattleTypeSelectPopover()

    def __handleFightButtonUpdated(self, _):
        self.__updatePrebattleControls()

    def __handleSetPrebattleCoolDown(self, event):
        prbDispatcher = g_prbLoader.getDispatcher()
        if not prbDispatcher:
            return
        playerInfo = prbDispatcher.getPlayerInfo()
        isCreator = playerInfo.isCreator
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE and not isCreator:
            self.as_setCoolDownForReadyS(event.coolDown)

    def __showBubbleTooltip(self, event):
        self.as_showBubbleTooltipS(event.getMessage(), event.getDuration())

    def __onVehicleChanged(self):
        self.__updatePrebattleControls()

    def __onEventsCacheResync(self):
        self.__updatePrebattleControls()
