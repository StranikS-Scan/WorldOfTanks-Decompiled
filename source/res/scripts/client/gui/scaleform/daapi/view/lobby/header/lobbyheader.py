# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/LobbyHeader.py
import math
import operator
import BigWorld
from CurrentVehicle import g_currentVehicle
import account_helpers
from account_helpers.AccountSettings import AccountSettings, BOOSTERS
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, REQUEST_TYPE, UNIT_RESTRICTION
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
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
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.server_events import g_eventsCache
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LobbyHeaderMeta import LobbyHeaderMeta
from gui.Scaleform.framework import g_entitiesFactories, ViewTypes, AppRef
from ConnectionManager import connectionManager
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.MENU import MENU
_MAX_HEADER_SERVER_NAME_LEN = 6
_SERVER_NAME_PREFIX = '%s..'

class TOOLTIP_TYPES(object):
    COMPLEX = 'complex'
    SPECIAL = 'special'
    NONE = 'none'


class LobbyHeader(LobbyHeaderMeta, AppRef, GlobalListener, ClanEmblemsHelper):

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
        self.addListener(events.CloseWindowEvent.GOLD_FISH_CLOSED, self.__onGoldFishWindowClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__setCredits,
         'stats.gold': self.__setGold,
         'stats.freeXP': self.__setFreeXP,
         'stats.clanInfo': self.__setClanInfo,
         'goodies': self.__updateGoodies,
         'account.premiumExpiryTime': self.__onPremiumExpireTimeChanged,
         'cache.SPA': self.__onSPAUpdated})
        self.as_setFightButtonS(i18n.makeString('#menu:headerButtons/battle'))
        self.as_setWalletStatusS(game_control.g_instance.wallet.componentsStatuses)
        self.updateAccountInfo()
        self.startGlobalListening()
        self.__updateServerName()
        if not isTimeToShowGoldFishPromo():
            enabledVal = isGoldFishActionActive()
            tooltip = TOOLTIPS.HEADER_REFILL_ACTION if enabledVal else TOOLTIPS.HEADER_REFILL
            self.as_setGoldFishEnabledS(enabledVal, False, tooltip, TOOLTIP_TYPES.COMPLEX)
        Waiting.hide('enter')

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if not self.isDisposed() and emblem:
            self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    def __updateServerName(self):
        serverShortName = connectionManager.serverUserNameShort.split()[-1].strip()
        if len(serverShortName) > _MAX_HEADER_SERVER_NAME_LEN:
            serverShortName = _SERVER_NAME_PREFIX % serverShortName[:_MAX_HEADER_SERVER_NAME_LEN]
        self.as_setServerS(serverShortName, 'settingsButton', TOOLTIP_TYPES.SPECIAL)

    def _dispose(self):
        battle_selector_items.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.BubbleTooltipEvent.SHOW, self.__showBubbleTooltip, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CloseWindowEvent.GOLD_FISH_CLOSED, self.__onGoldFishWindowClosed, scope=EVENT_BUS_SCOPE.LOBBY)
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
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PREMIUM_WINDOW))

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

    def __setClanInfo(self, clanInfo):
        name = BigWorld.player().name
        if clanInfo and len(clanInfo) > 1:
            clanAbbrev = clanInfo[1]
        else:
            clanAbbrev = None
        hasNew = not AccountSettings.getFilter(BOOSTERS)['wasShown']
        hasActiveBooster = len(g_goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE)) > 0
        self.as_nameResponseS(g_lobbyContext.getPlayerFullName(name, clanInfo=clanInfo), name, clanAbbrev, g_itemsCache.items.stats.isTeamKiller, g_clanCache.isInClan, hasNew, hasActiveBooster, TOOLTIPS.HEADER_ACCOUNT, TOOLTIP_TYPES.COMPLEX)
        if g_clanCache.clanDBID:
            self.requestClanEmblem32x32(g_clanCache.clanDBID)
        return

    def __onPremiumExpireTimeChanged(self, timestamp):
        self.updateAccountAttrs()

    def __setCredits(self, accCredits):
        self.as_creditsResponseS(BigWorld.wg_getIntegralFormat(accCredits), MENU.HEADERBUTTONS_BTNLABEL_EXCHANGE_GOLD, TOOLTIPS.HEADER_GOLD_EXCHANGE, TOOLTIP_TYPES.COMPLEX)

    def __setGold(self, gold):
        self.as_goldResponseS(BigWorld.wg_getGoldFormat(gold), MENU.HEADERBUTTONS_BTNLABEL_BUY_GOLD, TOOLTIPS.HEADER_REFILL, TOOLTIP_TYPES.COMPLEX)

    def __setFreeXP(self, freeXP):
        self.as_setFreeXPS(BigWorld.wg_getIntegralFormat(freeXP), MENU.HEADERBUTTONS_BTNLABEL_GATHERING_EXPERIENCE, TOOLTIPS.HEADER_XP_GATHERING, TOOLTIP_TYPES.COMPLEX)

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
            if not canUpdatePremium:
                disableTTHeader = i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_HEADER)
                disableTTBody = i18n.makeString(TOOLTIPS.LOBBY_HEADER_BUYPREMIUMACCOUNT_DISABLED_BODY, number=time_utils.ONE_YEAR / time_utils.ONE_DAY)
            self.as_doDisableHeaderButtonS(self.BUTTONS.PREM, canUpdatePremium)
            hasPersonalDiscount = len(g_itemsCache.items.shop.personalPremiumPacketsDiscounts) > 0
            tooltip = canUpdatePremium or {'header': disableTTHeader,
             'body': disableTTBody}
        else:
            tooltip = TOOLTIPS.HEADER_PREMIUM_EXTEND if isPremiumAccount else TOOLTIPS.HEADER_PREMIUM_BUY
        self.as_setPremiumParamsS(isPremiumAccount, premiumBtnLbl, buyPremiumLabel, canUpdatePremium, disableTTHeader, disableTTBody, hasPersonalDiscount, tooltip, TOOLTIP_TYPES.COMPLEX)

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
        self.as_setFreeXPS(BigWorld.wg_getIntegralFormat(g_itemsCache.items.stats.actualFreeXP))
        self.as_setWalletStatusS(status)

    def __onPremiumTimeChanged(self, isPremium, _, premiumExpiryTime):
        self.__setAccountsAttrs(isPremium, premiumExpiryTime=premiumExpiryTime)

    def __onViewAddedToContainer(self, _, pyEntity):
        settings = pyEntity.settings
        if settings.type is ViewTypes.LOBBY_SUB:
            if settings.alias in (VIEW_ALIAS.BATTLE_QUEUE, CYBER_SPORT_ALIASES.CS_RESPAWN_PY):
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

    def __getFightBtnTooltipData(self, state):
        eventVehicles = g_eventsCache.getEventVehicles()
        vehicleNames = ', '.join(map(operator.attrgetter('userName'), eventVehicles))
        if state == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
            header = i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_VEHICLENOTVALID_HEADER)
            body = i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_VEHICLENOTVALID_BODY)
            note = i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_GROUPNOTREADY_NOTE, vehicles=vehicleNames)
        else:
            header = i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_GROUPNOTREADY_HEADER)
            body = i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_GROUPNOTREADY_BODY)
            note = i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_GROUPNOTREADY_NOTE, vehicles=vehicleNames)
        return {'header': header,
         'body': body,
         'note': text_styles.alert(note)}

    def __updatePrebattleControls(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if not prbDispatcher:
            return
        else:
            items = battle_selector_items.getItems()
            state = prbDispatcher.getFunctionalState()
            selected = items.update(state)
            canDo, canDoMsg = prbDispatcher.canPlayerDoAction()
            playerInfo = prbDispatcher.getPlayerInfo()
            if selected.isInSquad(state):
                isInSquad = True
            else:
                isInSquad = False
                self.as_doDisableHeaderButtonS(self.BUTTONS.SQUAD, not state.hasLockedState)
            isFallout = g_eventsCache.isEventEnabled()
            if isInSquad:
                tooltip = TOOLTIPS.HEADER_SQUAD_MEMBER
            else:
                tooltip = TOOLTIPS.HEADER_DOMINATIONSQUAD if isFallout else TOOLTIPS.HEADER_SQUAD
            self.as_updateSquadS(isInSquad, tooltip, TOOLTIP_TYPES.COMPLEX)
            isFightBtnDisabled = not canDo or selected.isFightButtonForcedDisabled()
            isEventVehicle = g_currentVehicle.isPresent() and g_currentVehicle.item.isOnlyForEventBattles
            isInCompany = state.isInPrebattle(PREBATTLE_TYPE.COMPANY)
            if isFightBtnDisabled and isEventVehicle and not state.hasLockedState and not isInCompany:
                self.as_setFightBtnTooltipDataS(self.__getFightBtnTooltipData(canDoMsg))
            else:
                self.as_setFightBtnTooltipDataS(None)
            self.as_disableFightButtonS(isFightBtnDisabled)
            self.as_setFightButtonS(selected.getFightButtonLabel(state, playerInfo))
            self.as_updateBattleTypeS(i18n.makeString(selected.getLabel()), selected.getSmallIcon(), not selected.isDisabled(), TOOLTIPS.HEADER_BATTLETYPE, TOOLTIP_TYPES.COMPLEX)
            if selected.isDisabled():
                self.__closeBattleTypeSelectPopover()
            else:
                self.__updateBattleTypeSelectPopover()
            return

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

    def __updateGoodies(self, *args):
        self.updateClanInfo()
        self.updateAccountAttrs()

    def __onSPAUpdated(self, _):
        enabledVal = isGoldFishActionActive()
        tooltip = TOOLTIPS.HEADER_REFILL_ACTION if enabledVal else TOOLTIPS.HEADER_REFILL
        self.as_setGoldFishEnabledS(enabledVal, False, tooltip, TOOLTIP_TYPES.COMPLEX)

    def __onGoldFishWindowClosed(self, _):
        enabledVal = isGoldFishActionActive()
        tooltip = TOOLTIPS.HEADER_REFILL_ACTION if enabledVal else TOOLTIPS.HEADER_REFILL
        self.as_setGoldFishEnabledS(enabledVal, True, tooltip, TOOLTIP_TYPES.COMPLEX)
