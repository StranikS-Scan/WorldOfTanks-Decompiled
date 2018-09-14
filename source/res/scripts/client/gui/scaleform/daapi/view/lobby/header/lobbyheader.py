# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/LobbyHeader.py
import math
import BigWorld
from CurrentVehicle import g_currentVehicle
import account_helpers
from account_helpers.AccountSettings import AccountSettings, BOOSTERS
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control import getFalloutCtrl
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, REQUEST_TYPE, UNIT_RESTRICTION, PREBATTLE_RESTRICTION, QUEUE_RESTRICTION
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n, time_utils, int2roman
from debug_utils import LOG_ERROR
from shared_utils import CONST_CONTAINER, findFirst
from gui import makeHtmlString, game_control
from gui.LobbyContext import g_lobbyContext
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.context import PrebattleAction
from gui.shared import events
from gui.shared import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.ClanCache import g_clanCache
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.server_events import g_eventsCache
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LobbyHeaderMeta import LobbyHeaderMeta
from gui.Scaleform.framework import g_entitiesFactories, ViewTypes
from ConnectionManager import connectionManager
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.settings.tooltips import TOOLTIPS_CONSTANTS
_MAX_HEADER_SERVER_NAME_LEN = 6
_SERVER_NAME_PREFIX = '%s..'

class TOOLTIP_TYPES(object):
    COMPLEX = 'complex'
    SPECIAL = 'special'
    NONE = 'none'


class LobbyHeader(LobbyHeaderMeta, ClanEmblemsHelper, GlobalListener):

    class BUTTONS(CONST_CONTAINER):
        SETTINGS = 'settings'
        ACCOUNT = 'account'
        PREM = 'prem'
        SQUAD = 'squad'
        GOLD = 'gold'
        SILVER = 'silver'
        FREE_XP = 'freeXP'
        BATTLE_SELECTOR = 'battleSelector'

    def __init__(self):
        super(LobbyHeader, self).__init__()
        self.__falloutCtrl = None
        return

    def _populate(self):
        battle_selector_items.create()
        super(LobbyHeader, self)._populate()
        self.startGlobalListening()
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        game_control.g_instance.wallet.onWalletStatusChanged += self.__onWalletChanged
        game_control.g_instance.gameSession.onPremiumNotify += self.__onPremiumTimeChanged
        game_control.g_instance.igr.onIgrTypeChanged += self.__onIGRChanged
        g_lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_currentVehicle.onChanged += self.__onVehicleChanged
        g_eventsCache.onSyncCompleted += self.__onEventsCacheResync
        g_itemsCache.onSyncCompleted += self.__onItemsChanged
        self.__falloutCtrl = getFalloutCtrl()
        self.__falloutCtrl.onVehiclesChanged += self.__updateFalloutSettings
        self.__falloutCtrl.onSettingsChanged += self.__updateFalloutSettings
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
        self.__updateServerName()
        if not isTimeToShowGoldFishPromo():
            enabledVal = isGoldFishActionActive()
            tooltip = TOOLTIPS.HEADER_REFILL_ACTION if enabledVal else TOOLTIPS.HEADER_REFILL
            self.as_setGoldFishEnabledS(enabledVal, False, tooltip, TOOLTIP_TYPES.COMPLEX)
        Waiting.hide('enter')

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if not self.isDisposed() and emblem:
            self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__updatePrebattleControls()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__updatePrebattleControls()

    def onPrbFunctionalInited(self):
        self.__updatePrebattleControls()

    def onUnitFunctionalInited(self):
        self.__updatePrebattleControls()

    def onPrbFunctionalFinished(self):
        self.__updatePrebattleControls()

    def onUnitFunctionalFinished(self):
        self.__updatePrebattleControls()

    def onPreQueueFunctionalInited(self):
        self.__updatePrebattleControls()

    def onPreQueueFunctionalFinished(self):
        self.__updatePrebattleControls()

    def __updateServerName(self):
        serverShortName = connectionManager.serverUserNameShort.split()[-1].strip()
        if len(serverShortName) > _MAX_HEADER_SERVER_NAME_LEN:
            serverShortName = _SERVER_NAME_PREFIX % serverShortName[:_MAX_HEADER_SERVER_NAME_LEN]
        self.as_setServerS(serverShortName, TOOLTIPS_CONSTANTS.SETTINGS_BUTTON, TOOLTIP_TYPES.SPECIAL)

    def _dispose(self):
        battle_selector_items.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.stopGlobalListening()
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.BubbleTooltipEvent.SHOW, self.__showBubbleTooltip, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CloseWindowEvent.GOLD_FISH_CLOSED, self.__onGoldFishWindowClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        game_control.g_instance.gameSession.onPremiumNotify -= self.__onPremiumTimeChanged
        game_control.g_instance.wallet.onWalletStatusChanged -= self.__onWalletChanged
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onIGRChanged
        g_lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheResync
        g_itemsCache.onSyncCompleted -= self.__onItemsChanged
        self.__falloutCtrl.onVehiclesChanged -= self.__updateFalloutSettings
        self.__falloutCtrl.onSettingsChanged -= self.__updateFalloutSettings
        self.__falloutCtrl = None
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        super(LobbyHeader, self)._dispose()
        return

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
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.PREMIUM_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def fightClick(self, mapID, actionName):
        if self.prbDispatcher:
            self.prbDispatcher.doAction(PrebattleAction(actionName, mapID=mapID))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')

    def showSquad(self):
        if self.prbDispatcher:
            self.prbDispatcher.doSelectAction(PrebattleAction(PREBATTLE_ACTION_NAME.SQUAD))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')

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
        isActionActive = g_itemsCache.items.shop.isXPConversionActionActive
        self.as_setFreeXPS(BigWorld.wg_getIntegralFormat(freeXP), MENU.HEADERBUTTONS_BTNLABEL_GATHERING_EXPERIENCE, isActionActive, TOOLTIPS.HEADER_XP_GATHERING, TOOLTIP_TYPES.COMPLEX)

    def __setAccountsAttrs(self, isPremiumAccount, premiumExpiryTime = 0):
        disableTTHeader = ''
        disableTTBody = ''
        isNavigationEnabled = True
        if self.prbDispatcher:
            isNavigationEnabled = not self.prbDispatcher.getFunctionalState().isNavigationDisabled()
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
            self.as_doDisableHeaderButtonS(self.BUTTONS.PREM, canUpdatePremium and isNavigationEnabled)
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
        self.as_goldResponseS(BigWorld.wg_getGoldFormat(g_itemsCache.items.stats.actualGold), MENU.HEADERBUTTONS_BTNLABEL_BUY_GOLD, TOOLTIPS.HEADER_REFILL, TOOLTIP_TYPES.COMPLEX)
        self.as_setFreeXPS(BigWorld.wg_getIntegralFormat(g_itemsCache.items.stats.actualFreeXP), MENU.HEADERBUTTONS_BTNLABEL_GATHERING_EXPERIENCE, g_itemsCache.items.shop.isXPConversionActionActive, TOOLTIPS.HEADER_XP_GATHERING, TOOLTIP_TYPES.COMPLEX)
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
        falloutCtrl = getFalloutCtrl()
        config = falloutCtrl.getConfig()
        if state == PREBATTLE_RESTRICTION.VEHICLE_FALLOUT_ONLY:
            header = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutOnly/header')
            body = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutOnly/body')
        elif state == PREBATTLE_RESTRICTION.FALLOUT_NOT_SELECTED:
            header = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutNotSelected/header')
            body = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutNotSelected/body')
        elif state == PREBATTLE_RESTRICTION.VEHICLE_GROUP_IS_NOT_READY:
            header = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutNotReady/header')
            body = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutNotReady/body')
        elif state == UNIT_RESTRICTION.FALLOUT_NOT_ENOUGH_PLAYERS:
            header = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutNotEnoughPlayer/header')
            body = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutNotEnoughPlayer/body')
        elif state in (UNIT_RESTRICTION.FALLOUT_VEHICLE_LEVEL_REQUIRED, PREBATTLE_RESTRICTION.VEHICLE_GROUP_REQUIRED):
            header = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutVehLevelRequired/header')
            body = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutVehLevelRequired/body', level=int2roman(config.vehicleLevelRequired))
        elif state in (UNIT_RESTRICTION.FALLOUT_VEHICLE_MIN, PREBATTLE_RESTRICTION.VEHICLE_GROUP_MIN):
            allowedLevelsList = list(config.allowedLevels)
            if len(allowedLevelsList) > 1:
                header = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutVehMin/header')
                body = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutVehMin/body', min=str(config.minVehiclesPerPlayer), level=toRomanRangeString(allowedLevelsList, 1))
            else:
                header = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutVehLevelRequired/header')
                body = i18n.makeString('#menu:headerButtons/fightBtn/tooltip/falloutVehLevelRequired/body', level=int2roman(config.vehicleLevelRequired))
        else:
            return None
        return {'header': header,
         'body': body,
         'note': ''}

    def __getSandboxTooltipData(self):
        return {'header': i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_SANDBOX_INVALID_HEADER),
         'body': i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_SANDBOX_INVALID_LEVEL_BODY)}

    def __updatePrebattleControls(self):
        if not self.prbDispatcher:
            return
        else:
            items = battle_selector_items.getItems()
            state = self.prbDispatcher.getFunctionalState()
            selected = items.update(state)
            canDo, canDoMsg = self.prbDispatcher.canPlayerDoAction()
            playerInfo = self.prbDispatcher.getPlayerInfo()
            if selected.isInSquad(state):
                isInSquad = True
            else:
                isInSquad = False
                self.as_doDisableHeaderButtonS(self.BUTTONS.SQUAD, self.prbDispatcher.getFunctionalCollection().canCreateSquad())
            falloutCtrl = getFalloutCtrl()
            isFallout = falloutCtrl.isSelected()
            if isInSquad:
                tooltip = TOOLTIPS.HEADER_SQUAD_MEMBER
            else:
                tooltip = TOOLTIPS.HEADER_DOMINATIONSQUAD if isFallout else TOOLTIPS.HEADER_SQUAD
            self.as_updateSquadS(isInSquad, tooltip, TOOLTIP_TYPES.COMPLEX)
            isFightBtnDisabled = not canDo or selected.isFightButtonForcedDisabled()
            if isFightBtnDisabled and not state.hasLockedState:
                isEventVehicle = g_currentVehicle.isPresent() and g_currentVehicle.item.isEvent
                if state.isInPreQueue(queueType=QUEUE_TYPE.SANDBOX) and canDoMsg == QUEUE_RESTRICTION.LIMIT_LEVEL:
                    self.as_setFightBtnTooltipDataS(self.__getSandboxTooltipData())
                elif isEventVehicle and not state.isInPrebattle(PREBATTLE_TYPE.COMPANY) or isFallout:
                    self.as_setFightBtnTooltipDataS(self.__getFightBtnTooltipData(canDoMsg))
            else:
                self.as_setFightBtnTooltipDataS(None)
            self.as_disableFightButtonS(isFightBtnDisabled)
            self.as_setFightButtonS(selected.getFightButtonLabel(state, playerInfo))
            self.as_updateBattleTypeS(i18n.makeString(selected.getLabel()), selected.getSmallIcon(), not selected.isDisabled(), TOOLTIPS.HEADER_BATTLETYPE, TOOLTIP_TYPES.COMPLEX, selected.getData())
            if selected.isDisabled():
                self.__closeBattleTypeSelectPopover()
            else:
                self.__updateBattleTypeSelectPopover()
            isNavigationEnabled = not state.isNavigationDisabled()
            self.as_doDisableHeaderButtonS(self.BUTTONS.SILVER, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.GOLD, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.FREE_XP, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.ACCOUNT, isNavigationEnabled)
            self.updateAccountAttrs()
            return

    def __handleFightButtonUpdated(self, _):
        self.__updatePrebattleControls()

    def __handleSetPrebattleCoolDown(self, event):
        if not self.prbDispatcher:
            return
        playerInfo = self.prbDispatcher.getPlayerInfo()
        isCreator = playerInfo.isCreator
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE and not isCreator:
            self.as_setCoolDownForReadyS(event.coolDown)

    def __showBubbleTooltip(self, event):
        self.as_showBubbleTooltipS(event.getMessage(), event.getDuration())

    def __onVehicleChanged(self, *args):
        self.__updatePrebattleControls()

    def __onEventsCacheResync(self):
        self.__updatePrebattleControls()

    def __updateFalloutSettings(self, *args):
        self.__updatePrebattleControls()

    def __onIGRChanged(self, *args):
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

    def __onItemsChanged(self, updateReason, invalidItems):
        vehiclesDiff = invalidItems.get(GUI_ITEM_TYPE.VEHICLE)
        if vehiclesDiff is not None:
            falloutVehicle = findFirst(lambda v: v.intCD in vehiclesDiff, getFalloutCtrl().getSelectedVehicles())
            if falloutVehicle is not None:
                self.__updatePrebattleControls()
        return

    def __onServerSettingChanged(self, diff):
        if 'isSandboxEnabled' in diff:
            self.__updatePrebattleControls()
