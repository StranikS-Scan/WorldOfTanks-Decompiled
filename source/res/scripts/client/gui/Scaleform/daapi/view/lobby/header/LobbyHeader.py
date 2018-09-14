# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/LobbyHeader.py
import math
import BigWorld
import constants
import account_helpers
from account_helpers.settings_core import g_settingsCore
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from account_helpers.AccountSettings import AccountSettings, BOOSTERS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control import getFalloutCtrl
from gui.game_control.ServerStats import STATS_TYPE
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.goodies import g_goodiesCache
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, REQUEST_TYPE, UNIT_RESTRICTION, PREBATTLE_RESTRICTION, QUEUE_RESTRICTION
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import i18n, time_utils, int2roman, isPlayerAccount
from debug_utils import LOG_ERROR
from predefined_hosts import g_preDefinedHosts, getPingStatus, UNDEFINED_PING_VAL
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
from gui.shared.utils.functions import makeTooltip
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
_MAX_BOOSTERS_TO_DISPLAY = 99
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
        PREMSHOP = 'premShop'
        SQUAD = 'squad'
        GOLD = 'gold'
        SILVER = 'silver'
        FREE_XP = 'freeXP'
        BATTLE_SELECTOR = 'battleSelector'

    class TABS(CONST_CONTAINER):
        HANGAR = 'hangar'
        PROFILE = 'profile'
        TECHTREE = 'techtree'
        BARRACKS = 'barracks'
        PREBATTLE = 'prebattle'
        BROWSER = 'browser'
        RESEARCH = 'research'
        ACADEMY = 'academy'

    def __init__(self):
        super(LobbyHeader, self).__init__()
        self.__falloutCtrl = None
        return

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if not self.isDisposed() and emblem:
            self.as_setClanEmblemS(self.getMemoryTexturePath(emblem))

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__updatePrebattleControls()

    def onUnitPlayerStateChanged(self, pInfo):
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

    def updateAccountInfo(self):
        self.updateMoneyStats()
        self.updateXPInfo()
        self.updateClanInfo()
        self.updateAccountAttrs()

    def updateMoneyStats(self):
        money = g_itemsCache.items.stats.actualMoney
        self.__setCredits(money.credits)
        self.__setGold(money.gold)

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

    def onPremShopClick(self):
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.PREM_SHOP))

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

    def _populate(self):
        self.__updateHangarMenuData()
        battle_selector_items.create()
        super(LobbyHeader, self)._populate()
        self.startGlobalListening()
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        game_control.g_instance.wallet.onWalletStatusChanged += self.__onWalletChanged
        game_control.g_instance.gameSession.onPremiumNotify += self.__onPremiumTimeChanged
        game_control.g_instance.igr.onIgrTypeChanged += self.__onIGRChanged
        g_lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_currentVehicle.onChanged += self.__onVehicleChanged
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        g_eventsCache.onSyncCompleted += self.__onEventsCacheResync
        g_itemsCache.onSyncCompleted += self.__onItemsChanged
        game_control.g_instance.boosters.onBoosterChangeNotify += self.__onUpdateGoodies
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
        self.as_setPremShopDataS(RES_ICONS.MAPS_ICONS_LOBBY_ICON_PREMSHOP, MENU.HEADERBUTTONS_BTNLABEL_PREMSHOP, TOOLTIPS.HEADER_PREMSHOP, TOOLTIP_TYPES.COMPLEX)
        self.as_initOnlineCounterS(constants.IS_SHOW_SERVER_STATS)
        game_control.g_instance.serverStats.onStatsReceived += self.__onStatsReceived
        self.updateAccountInfo()
        self.__updateServerData()
        self.__onStatsReceived()
        if not isTimeToShowGoldFishPromo():
            enabledVal = isGoldFishActionActive()
            tooltip = TOOLTIPS.HEADER_REFILL_ACTION if enabledVal else TOOLTIPS.HEADER_REFILL
            self.as_setGoldFishEnabledS(enabledVal, False, tooltip, TOOLTIP_TYPES.COMPLEX)
        g_preDefinedHosts.onPingPerformed += self.__onPingPerformed
        g_preDefinedHosts.requestPing()
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        encyclopediaController = game_control.getEncyclopediaController()
        encyclopediaController.onNewRecommendationReceived += self.__onNewEncyclopediaRecommendation
        encyclopediaController.onStateChanged += self.__updateHangarMenuData
        Waiting.hide('enter')

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
        g_lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheResync
        g_itemsCache.onSyncCompleted -= self.__onItemsChanged
        self.__falloutCtrl.onVehiclesChanged -= self.__updateFalloutSettings
        self.__falloutCtrl.onSettingsChanged -= self.__updateFalloutSettings
        self.__falloutCtrl = None
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        game_control.g_instance.serverStats.onStatsReceived -= self.__onStatsReceived
        game_control.g_instance.boosters.onBoosterChangeNotify -= self.__onUpdateGoodies
        g_preDefinedHosts.onPingPerformed -= self.__onPingPerformed
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        encyclopediaController = game_control.getEncyclopediaController()
        encyclopediaController.onStateChanged -= self.__updateHangarMenuData
        encyclopediaController.onNewRecommendationReceived -= self.__onNewEncyclopediaRecommendation
        super(LobbyHeader, self)._dispose()
        return

    def __updateServerData(self):
        serverShortName = connectionManager.serverUserNameShort.strip().split(' ')[-1]
        if len(serverShortName) > _MAX_HEADER_SERVER_NAME_LEN:
            serverShortName = _SERVER_NAME_PREFIX % serverShortName[:_MAX_HEADER_SERVER_NAME_LEN]
        self.as_setServerS(serverShortName, TOOLTIPS_CONSTANTS.SETTINGS_BUTTON, TOOLTIP_TYPES.SPECIAL)

    def __updateServerName(self):
        serverShortName = connectionManager.serverUserNameShort.strip().split(' ')[-1]
        if len(serverShortName) > _MAX_HEADER_SERVER_NAME_LEN:
            serverShortName = _SERVER_NAME_PREFIX % serverShortName[:_MAX_HEADER_SERVER_NAME_LEN]
        self.as_setServerS(serverShortName, TOOLTIPS_CONSTANTS.SETTINGS_BUTTON, TOOLTIP_TYPES.SPECIAL)

    def __setClanInfo(self, clanInfo):
        if not isPlayerAccount():
            return
        else:
            name = BigWorld.player().name
            if clanInfo and len(clanInfo) > 1:
                clanAbbrev = clanInfo[1]
            else:
                clanAbbrev = None
            hasNew = not AccountSettings.getFilter(BOOSTERS)['wasShown']
            activeBoosters = g_goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values()
            hasActiveBooster = len(activeBoosters) > 0
            readyBoosters = g_goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IS_READY_TO_ACTIVATE).values()
            boostersAvailable = sum((booster.count for booster in readyBoosters))
            hasAvailableBoosters = boostersAvailable > 0
            boosterIcon, boosterText = (None, None)
            if hasActiveBooster:
                boosterIcon = RES_ICONS.MAPS_ICONS_BOOSTERS_ACTIVEBOOSTERICON
                booster = sorted(activeBoosters, key=lambda x: x.getUsageLeftTime())[0]
                boosterText = booster.getShortLeftTimeStr()
            elif hasAvailableBoosters:
                boosterIcon = RES_ICONS.MAPS_ICONS_BOOSTERS_AVAILABLEBOOSTERICON
                if boostersAvailable <= _MAX_BOOSTERS_TO_DISPLAY:
                    boosterText = str(boostersAvailable)
                else:
                    boosterText = str(_MAX_BOOSTERS_TO_DISPLAY) + '+'
            self.as_nameResponseS({'userVO': {'fullName': g_lobbyContext.getPlayerFullName(name, clanInfo=clanInfo),
                        'userName': name,
                        'clanAbbrev': clanAbbrev},
             'isTeamKiller': g_itemsCache.items.stats.isTeamKiller,
             'hasNew': hasNew,
             'hasActiveBooster': hasActiveBooster,
             'hasAvailableBoosters': hasAvailableBoosters,
             'tooltip': TOOLTIPS.HEADER_ACCOUNT,
             'tooltipType': TOOLTIP_TYPES.COMPLEX,
             'boosterIcon': boosterIcon,
             'boosterBg': RES_ICONS.MAPS_ICONS_BOOSTERS_ACTIVEBOOSTERBG,
             'boosterText': boosterText})
            if g_clanCache.clanDBID:
                self.requestClanEmblem32x32(g_clanCache.clanDBID)
            else:
                self.as_setClanEmblemS(None)
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

    def __setAccountsAttrs(self, isPremiumAccount, premiumExpiryTime=0):
        if isPremiumAccount:
            assert premiumExpiryTime > 0
            deltaInSeconds = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(premiumExpiryTime)))
            if deltaInSeconds > time_utils.ONE_DAY:
                timeLeft = math.ceil(deltaInSeconds / time_utils.ONE_DAY)
                timeMetric = i18n.makeString('#menu:header/account/premium/days')
            else:
                timeLeft = math.ceil(deltaInSeconds / time_utils.ONE_HOUR)
                timeMetric = i18n.makeString('#menu:header/account/premium/hours')
            premiumBtnLbl = makeHtmlString('html_templates:lobby/header', 'premium-account-label', {'timeMetric': timeMetric,
             'timeLeft': timeLeft})
            canUpdatePremium = deltaInSeconds < time_utils.ONE_YEAR
            buyPremiumLabel = ''
            if canUpdatePremium:
                buyPremiumLabel = i18n.makeString('#menu:headerButtons/doLabel/premium')
        else:
            canUpdatePremium = True
            premiumBtnLbl = makeHtmlString('html_templates:lobby/header', 'base-account-label')
            buyPremiumLabel = i18n.makeString('#menu:common/premiumBuy')
        hasPersonalDiscount = len(g_itemsCache.items.shop.personalPremiumPacketsDiscounts) > 0
        if not canUpdatePremium:
            tooltip = formatters.getLimitExceededPremiumTooltip()
        elif isPremiumAccount:
            tooltip = TOOLTIPS.HEADER_PREMIUM_EXTEND
        else:
            tooltip = TOOLTIPS.HEADER_PREMIUM_BUY
        self.as_setPremiumParamsS(premiumBtnLbl, buyPremiumLabel, hasPersonalDiscount, tooltip, TOOLTIP_TYPES.COMPLEX)

    def __triggerViewLoad(self, alias):
        if alias == 'browser':
            game_control.getChinaCtrl().showBrowser()
        else:
            if alias == self.TABS.ACADEMY:
                self.as_removeButtonCounterS(alias)
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

    def __getSquadTypeSelectPopover(self):
        container = self.app.containerManager.getContainer(ViewTypes.WINDOW)
        view = None
        if container:
            view = container.getView({POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.SQUAD_TYPE_SELECT_POPOVER})
        return view

    def __closeBattleTypeSelectPopover(self):
        view = self.__getBattleTypeSelectPopover()
        if view:
            view.destroy()

    def __closeSquadTypeSelectPopover(self):
        view = self.__getSquadTypeSelectPopover()
        if view:
            view.destroy()

    def __updateBattleTypeSelectPopover(self):
        view = self.__getBattleTypeSelectPopover()
        if view:
            view.update()

    def __updateSquadTypeSelectPopover(self):
        view = self.__getSquadTypeSelectPopover()
        if view:
            view.update()

    def __getEventTooltipData(self):
        header = i18n.makeString(TOOLTIPS.EVENT_SQUAD_DISABLE_HEADER)
        vehicle = g_eventsCache.getEventVehicles()[0]
        body = i18n.makeString(TOOLTIPS.EVENT_SQUAD_DISABLE_BODY, tankName=vehicle.shortUserName)
        return makeTooltip(header, body)

    def __getSquadFightBtnTooltipData(self, state):
        if state == UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED:
            header = i18n.makeString(TOOLTIPS.HANGAR_STARTBTN_SQUADNOTREADY_HEADER)
            body = i18n.makeString(TOOLTIPS.HANGAR_STARTBTN_SQUADNOTREADY_BODY)
        elif state == UNIT_RESTRICTION.VEHICLE_INVALID_LEVEL:
            header = i18n.makeString(TOOLTIPS.HANGAR_TANKCARUSEL_WRONGSQUADVEHICLE_HEADER)
            body = i18n.makeString(TOOLTIPS.HANGAR_TANKCARUSEL_WRONGSQUADVEHICLE_BODY)
        else:
            return None
        return makeTooltip(header, body)

    def __getFalloutFightBtnTooltipData(self, state):
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
        return makeTooltip(header, body)

    def __getSandboxTooltipData(self):
        return {makeTooltip(i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_SANDBOX_INVALID_HEADER), i18n.makeString(MENU.HEADERBUTTONS_FIGHTBTN_TOOLTIP_SANDBOX_INVALID_LEVEL_BODY))}

    def __updatePrebattleControls(self):
        if not self.prbDispatcher:
            return
        else:
            items = battle_selector_items.getItems()
            suadItems = battle_selector_items.getSquadItems()
            state = self.prbDispatcher.getFunctionalState()
            selected = items.update(state)
            squadSelected = suadItems.update(state)
            canDo, canDoMsg = self.prbDispatcher.canPlayerDoAction()
            playerInfo = self.prbDispatcher.getPlayerInfo()
            if selected.isInSquad(state):
                isInSquad = True
            else:
                isInSquad = False
                self.as_doDisableHeaderButtonS(self.BUTTONS.SQUAD, self.prbDispatcher.getFunctionalCollection().canCreateSquad())
            falloutCtrl = getFalloutCtrl()
            isFallout = falloutCtrl.isSelected()
            isEvent = g_eventsCache.isEventEnabled()
            if isInSquad:
                tooltip = TOOLTIPS.HEADER_SQUAD_MEMBER
            elif isFallout:
                tooltip = TOOLTIPS.HEADER_DOMINATIONSQUAD
            elif isEvent:
                tooltip = TOOLTIPS.HEADER_SQUAD_MEMBER
            else:
                tooltip = TOOLTIPS.HEADER_SQUAD
            if state.isInUnit(constants.PREBATTLE_TYPE.EVENT):
                iconSquad = RES_ICONS.MAPS_ICONS_BATTLETYPES_40X40_EVENTSQUAD
            else:
                iconSquad = RES_ICONS.MAPS_ICONS_BATTLETYPES_40X40_SQUAD
            self.as_updateSquadS(isInSquad, tooltip, TOOLTIP_TYPES.COMPLEX, isEvent, iconSquad)
            isFightBtnDisabled = not canDo or selected.isFightButtonForcedDisabled()
            if isFightBtnDisabled and not state.hasLockedState:
                if state.isInPreQueue(queueType=constants.QUEUE_TYPE.SANDBOX) and canDoMsg == QUEUE_RESTRICTION.LIMIT_LEVEL:
                    self.as_setFightBtnTooltipS(self.__getSandboxTooltipData())
                elif isFallout:
                    self.as_setFightBtnTooltipS(self.__getFalloutFightBtnTooltipData(canDoMsg))
                elif isEvent and state.isInUnit(constants.PREBATTLE_TYPE.EVENT):
                    self.as_setFightBtnTooltipS(self.__getEventTooltipData())
                elif isInSquad:
                    self.as_setFightBtnTooltipS(self.__getSquadFightBtnTooltipData(canDoMsg))
                else:
                    self.as_setFightBtnTooltipS(None)
            else:
                self.as_setFightBtnTooltipS(None)
            self.as_disableFightButtonS(isFightBtnDisabled)
            self.as_setFightButtonS(selected.getFightButtonLabel(state, playerInfo))
            self.as_updateBattleTypeS(i18n.makeString(selected.getLabel()), selected.getSmallIcon(), selected.isSelectorBtnEnabled(), TOOLTIPS.HEADER_BATTLETYPE, TOOLTIP_TYPES.COMPLEX, selected.getData())
            if selected.isDisabled():
                self.__closeBattleTypeSelectPopover()
            else:
                self.__updateBattleTypeSelectPopover()
            if squadSelected.isDisabled():
                self.__closeSquadTypeSelectPopover()
            else:
                self.__updateSquadTypeSelectPopover()
            isNavigationEnabled = not state.isNavigationDisabled()
            self.as_doDisableHeaderButtonS(self.BUTTONS.PREM, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.SILVER, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.GOLD, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.FREE_XP, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.ACCOUNT, isNavigationEnabled)
            self.as_doDisableHeaderButtonS(self.BUTTONS.PREMSHOP, isNavigationEnabled)
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
        self.updateXPInfo()
        self.updateAccountAttrs()

    def __updateHangarMenuData(self):
        tabDataProvider = [{'label': MENU.HEADERBUTTONS_HANGAR,
          'value': self.TABS.HANGAR,
          'textColor': 16764006,
          'textColorOver': 16768409,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_HANGAR},
         {'label': MENU.HEADERBUTTONS_SHOP,
          'value': STORE_CONSTANTS.STORE,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_SHOP},
         {'label': MENU.HEADERBUTTONS_PROFILE,
          'value': self.TABS.PROFILE,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_PROFILE},
         {'label': MENU.HEADERBUTTONS_TECHTREE,
          'value': self.TABS.TECHTREE,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_TECHTREE,
          'subValues': [self.TABS.RESEARCH]},
         {'label': MENU.HEADERBUTTONS_BARRACKS,
          'value': self.TABS.BARRACKS,
          'tooltip': TOOLTIPS.HEADER_BUTTONS_BARRACKS}]
        if constants.IS_CHINA:
            tabDataProvider.append({'label': MENU.HEADERBUTTONS_BROWSER,
             'value': self.TABS.BROWSER,
             'tooltip': TOOLTIPS.HEADER_BUTTONS_BROWSER})
        fortEnabled = g_lobbyContext.getServerSettings().isFortsEnabled()
        if fortEnabled:
            tooltip = TOOLTIPS.HEADER_BUTTONS_FORTS
        else:
            tooltip = TOOLTIPS.HEADER_BUTTONS_FORTS_TURNEDOFF
        tabDataProvider.append({'label': MENU.HEADERBUTTONS_FORTS,
         'value': FORTIFICATION_ALIASES.FORTIFICATIONS_VIEW_ALIAS,
         'tooltip': tooltip,
         'enabled': fortEnabled})
        encyclopediaCtrl = game_control.getEncyclopediaController()
        if encyclopediaCtrl.isActivated():
            tabDataProvider.append({'label': MENU.HEADERBUTTONS_ENCYCLOPEDIA,
             'value': self.TABS.ACADEMY,
             'tooltip': TOOLTIPS.HEADER_BUTTONS_ENCYCLOPEDIA})
        self.as_setHangarMenuDataS({'tabDataProvider': tabDataProvider})
        if encyclopediaCtrl.isActivated() and encyclopediaCtrl.hasNewRecommendations():
            self.__onNewEncyclopediaRecommendation()

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
        if 'isFortsEnabled' in diff:
            self.__updateHangarMenuData()
            self.__updatePrebattleControls()

    def __onUpdateGoodies(self, *args):
        self.__setClanInfo(g_clanCache.clanInfo)

    def __onPingPerformed(self, result):
        """
        g_preDefinedHosts.onPingPerformed event handler
        :param result: [dict] key - periphery id, value - ping value.
        """
        self.__updatePing(result)

    def __onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            self.__updatePing(g_preDefinedHosts.getPingResult())

    def __updatePing(self, pingValues):
        currentPing = pingValues.get(connectionManager.url, UNDEFINED_PING_VAL)
        self.as_updatePingStatusS(getPingStatus(currentPing), g_settingsCore.getSetting('isColorBlind'))

    def __setCounter(self, alias):
        text = i18n.makeString(MENU.HEADER_NOTIFICATIONSIGN)
        self.as_setButtonCounterS(alias, text_styles.counterLabelText(text))

    def __onNewEncyclopediaRecommendation(self):
        if game_control.getEncyclopediaController().isActivated():
            self.__setCounter(self.TABS.ACADEMY)

    def __onStatsReceived(self):
        """ Fill up the data required for online stats and send to flash.
        """
        clusterUsers, regionUsers, tooltipType = game_control.g_instance.serverStats.getStats()
        if tooltipType == STATS_TYPE.UNAVAILABLE:
            tooltip = TOOLTIPS.HEADER_INFO_PLAYERS_UNAVAILABLE
            clusterUsers = regionUsers = ''
        elif tooltipType == STATS_TYPE.CLUSTER:
            tooltip = TOOLTIPS.HEADER_INFO_PLAYERS_ONLINE_REGION
        else:
            tooltip = TOOLTIPS.HEADER_INFO_PLAYERS_ONLINE_FULL
        clusterStats = makeHtmlString('html_templates:lobby', 'onlineCounter', {'key': connectionManager.serverUserNameShort,
         'value': clusterUsers})
        if tooltipType == STATS_TYPE.FULL:
            regionStats = makeHtmlString('html_templates:lobby', 'onlineCounter', {'key': i18n.makeString(MENU.ONLINECOUNTER_TOTAL),
             'value': regionUsers})
        else:
            regionStats = ''
        body = i18n.makeString('{}/body'.format(tooltip), servername=connectionManager.serverUserName)
        header = '{}/header'.format(tooltip)
        isAvailable = tooltipType != STATS_TYPE.UNAVAILABLE
        self.as_updateOnlineCounterS(clusterStats, regionStats, makeTooltip(header, body), isAvailable)
