# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
import logging
from operator import attrgetter
import typing
from BWUtil import AsyncReturn
import adisp
from CurrentVehicle import HeroTankPreviewAppearance
from async import async, await
from constants import GameSeasonType, RentType
from debug_utils import LOG_WARNING
from frameworks.wulf import ViewFlags, Window, WindowFlags, WindowLayer, WindowStatus
from gui import DialogsInterface, GUI_SETTINGS, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nConfirmDialogMeta, I18nInfoDialogMeta
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getClanQuestURL
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyCollectibleVehiclesUrl, getClientControlledCloseCtx, getRentVehicleUrl, getShopURL, getTelecomRentVehicleUrl
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, SFViewLoadParams
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.genConsts.MAPBOX_ALIASES import MAPBOX_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.account_completion.utils.common import AccountCompletionType
from gui.impl.lobby.account_completion.utils.decorators import waitShowOverlay
from gui.impl.lobby.common.congrats.common_congrats_view import CongratsWindow
from gui.impl.lobby.maps_training.maps_training_queue_view import MapsTrainingQueueView
from gui.impl.lobby.tank_setup.dialogs.confirm_dialog import TankSetupConfirmDialog, TankSetupExitConfirmDialog
from gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepair
from gui.impl.lobby.tank_setup.dialogs.refill_shells import ExitFromShellsConfirm, RefillShells
from gui.impl.pub.lobby_window import LobbyNotificationWindow, LobbyWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared import events, g_eventBus
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getUserName
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getUniqueViewName, getViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shop import showBlueprintsExchangeOverlay, showBuyGoldForRentWebOverlay, showBuyProductOverlay
from helpers import dependency
from helpers.aop import pointcutable
from items import ITEM_TYPES, parseIntCompactDescr, vehicles as vehicles_core
from nations import NAMES
from shared_utils import first
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBrowserController, IClanNotificationController, IHeroTankController, IMarathonEventsController, IReferralProgramController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from uilogging.veh_post_progression.loggers import VehPostProgressionEntryPointLogger
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Generator, Iterable, List
    from gui.marathon.marathon_event import MarathonEvent
    from gui.Scaleform.framework.managers import ContainerManager
    from gui.shared.money import Money
_logger = logging.getLogger(__name__)

class SettingsTabIndex(object):
    GAME = 0
    GRAPHICS = 1
    SOUND = 2
    CONTROL = 3
    AIM = 4
    MARKERS = 5
    FEEDBACK = 6


def showBattleResultsWindow(arenaUniqueID):
    window = SFWindow(SFViewLoadParams(VIEW_ALIAS.BATTLE_RESULTS, getViewName(VIEW_ALIAS.BATTLE_RESULTS, str(arenaUniqueID))), EVENT_BUS_SCOPE.LOBBY, ctx={'arenaUniqueID': arenaUniqueID})
    window.load()
    return window


def notifyBattleResultsPosted(arenaUniqueID):
    g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.BATTLE_RESULTS_POSTED, {'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)


def showRankedBattleResultsWindow(rankedResultsVO, rankInfo, questsProgress, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, parent=parent), ctx={'rankedResultsVO': rankedResultsVO,
     'rankInfo': rankInfo,
     'questsProgress': questsProgress}), EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showRankedAwardWindow(awardsSequence, rankedInfo, notificationMgr=None):
    alias = RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD
    window = SFWindow(SFViewLoadParams(alias, getUniqueViewName(alias)), ctx={'awardsSequence': awardsSequence,
     'rankedInfo': rankedInfo}, scope=EVENT_BUS_SCOPE.LOBBY)
    notificationMgr.append(WindowNotificationCommand(window))


def showRankedPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showRankedBattleIntro():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS)), scope=EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_PRIME_TIME_ALIAS), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesAfterBattleWindow(reusableInfo, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS, parent=parent), ctx={'reusableInfo': reusableInfo}), EVENT_BUS_SCOPE.LOBBY)


def showBattleRoyaleLevelUpWindow(reusableInfo, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.LEVEL_UP, parent=parent), ctx={'reusableInfo': reusableInfo}), EVENT_BUS_SCOPE.LOBBY)


def showBattleRoyalePrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showBattleRoyaleResultsView(ctx):
    from gui.impl.lobby.battle_royale.battle_result_view import BrBattleResultsViewInLobby
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.battle_royale.BattleResultView()
    battleResultView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if battleResultView is not None:
        if battleResultView.arenaUniqueID == ctx.get('arenaUniqueID', -1):
            return
        battleResultView.destroyWindow()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, BrBattleResultsViewInLobby, ScopeTemplates.LOBBY_SUB_SCOPE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showHangarVehicleConfigurator(isFirstEnter=False):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW), ctx={'isFirstEnter': isFirstEnter}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleInfo(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEHICLE_INFO_WINDOW, getViewName(VIEW_ALIAS.VEHICLE_INFO_WINDOW, int(vehTypeCompDescr))), ctx={'vehicleCompactDescr': int(vehTypeCompDescr)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleRentDialog(intCD, rentType, nums, seasonType, price, buyParams):
    if not (seasonType == GameSeasonType.EPIC and rentType in (RentType.SEASON_RENT, RentType.SEASON_CYCLE_RENT)):
        _logger.debug('GameSeasonType %s with RentType %s is not supported', seasonType, rentType)
        return
    _purchaseOffer(intCD, rentType, nums, price, seasonType, buyParams, renew=False)


@adisp.process
@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _purchaseOffer(vehicleCD, rentType, nums, price, seasonType, buyParams, renew, itemsCache=None):
    from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsWebProductMeta
    if mayObtainForMoney(price):
        _doPurchaseOffer(vehicleCD, rentType, nums, price, seasonType, buyParams, renew)
    elif mayObtainWithMoneyExchange(price):
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsWebProductMeta(name=vehicle.shortUserName if vehicle else '', count=1, price=price.get(Currency.CREDITS)))
        if isOk:
            _doPurchaseOffer(vehicleCD, rentType, nums, price, seasonType, buyParams, renew)
    elif price.getCurrency() == Currency.GOLD:
        showBuyGoldForRentWebOverlay(price.get(Currency.GOLD), vehicleCD)
    else:
        vehicleName = getUserName(vehicles_core.getVehicleType(vehicleCD))
        SystemMessages.pushMessage(backport.text(R.strings.system_messages.vehicle_rent.dyn('not_enough_{}'.format(price.getCurrency()))(), vehName=vehicleName), type=SystemMessages.SM_TYPE.Error)


@adisp.process
def _doPurchaseOffer(vehicleCD, rentType, nums, price, seasonType, buyParams, renew):
    from gui.Scaleform.daapi.view.dialogs.rent_confirm_dialog import RentConfirmDialogMeta
    requestConfirmed = yield DialogsInterface.showDialog(meta=RentConfirmDialogMeta(vehicleCD, rentType, nums, price, seasonType, renew))
    if requestConfirmed:
        if mayObtainForMoney(price):
            showBuyProductOverlay(buyParams)
        else:
            _purchaseOffer(vehicleCD, rentType, nums, price, seasonType, buyParams, renew)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def mayObtainWithMoneyExchange(itemPrice, itemsCache=None):
    return itemPrice <= itemsCache.items.stats.money.exchange(Currency.GOLD, Currency.CREDITS, itemsCache.items.shop.exchangeRate, default=0)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def mayObtainForMoney(itemPrice, itemsCache=None):
    return itemPrice <= itemsCache.items.stats.money


def _getModuleInfoViewName(itemCD, vehicleDescr=None):
    itemTypeID, _, _ = parseIntCompactDescr(itemCD)
    return getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, itemCD, vehicleDescr.type.compactDescr if vehicleDescr is not None else '') if itemTypeID == ITEM_TYPES.vehicleGun else getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, itemCD)


def showModuleInfo(itemCD, vehicleDescr):
    itemCD = int(itemCD)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MODULE_INFO_WINDOW, _getModuleInfoViewName(itemCD, vehicleDescr)), ctx={'moduleCompactDescr': itemCD,
     'vehicleDescr': vehicleDescr}), EVENT_BUS_SCOPE.LOBBY)


def showStorageModuleInfo(intCD):
    intCD = int(intCD)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MODULE_INFO_WINDOW, _getModuleInfoViewName(intCD)), ctx={'moduleCompactDescr': intCD}), EVENT_BUS_SCOPE.LOBBY)


def showStorageBoosterInfo(boosterID):
    boosterID = int(boosterID)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOSTER_INFO_WINDOW, getViewName(VIEW_ALIAS.BOOSTER_INFO_WINDOW, boosterID)), ctx={'boosterID': boosterID}), EVENT_BUS_SCOPE.LOBBY)


def showDemountKitInfo(demountKitID):
    demountKitID = int(demountKitID)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.DEMOUNT_KIT_INFO_WINDOW, getViewName(VIEW_ALIAS.DEMOUNT_KIT_INFO_WINDOW, demountKitID)), ctx={'demountKitID': demountKitID}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleSellDialog(vehInvID):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEHICLE_SELL_DIALOG), ctx={'vehInvID': int(vehInvID)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleBuyDialog(vehicle, actionType=None, isTradeIn=False, previousAlias=None, showOnlyCongrats=False, returnAlias=None, returnCallback=None, ctx=None):
    from gui.impl.lobby.buy_vehicle_view import BuyVehicleWindow
    ctx = ctx or {}
    ctx.update({'nationID': vehicle.nationID,
     'itemID': vehicle.innationID,
     'actionType': actionType,
     'isTradeIn': isTradeIn,
     'previousAlias': previousAlias,
     'showOnlyCongrats': showOnlyCongrats,
     'returnAlias': returnAlias,
     'returnCallback': returnCallback})
    window = BuyVehicleWindow(ctx=ctx)
    window.load()
    if showOnlyCongrats:
        window.showCongratulations()


def showCongrats(context):
    CongratsWindow(context).load()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def showBlueprintView(vehicleCD, exitEvent=None, itemsCache=None):
    from gui.impl.lobby.blueprints.blueprint_screen import BlueprintScreen
    exitEvent = exitEvent or events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={'nation': itemsCache.items.getItemByCD(vehicleCD).nationName,
     'blueprintMode': True})
    _killOldView(R.views.lobby.blueprints.blueprint_screen.blueprint_screen.BlueprintScreen())
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.blueprints.blueprint_screen.blueprint_screen.BlueprintScreen(), BlueprintScreen, ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'vehicleCD': vehicleCD,
     'exitEvent': exitEvent}), scope=EVENT_BUS_SCOPE.LOBBY)


def showChangeVehicleNationDialog(vehicleCD):
    from gui.impl.lobby.nation_change.nation_change_screen import NationChangeScreen
    window = LobbyWindow(WindowFlags.WINDOW, content=NationChangeScreen(R.views.lobby.nation_change.nation_change_screen.NationChangeScreen(), ctx={'vehicleCD': vehicleCD}))
    window.load()


def showPiggyBankView():
    import BigWorld
    lobbyContext = dependency.instance(ILobbyContext)
    isWotPlusEnabled = lobbyContext.getServerSettings().isRenewableSubEnabled()
    isWotPlusNSEnabled = lobbyContext.getServerSettings().isWotPlusNewSubscriptionEnabled()
    hasWotPlusActive = BigWorld.player().renewableSubscription.isEnabled()
    hasGold = BigWorld.player().renewableSubscription.getGoldReserve()
    showNewPiggyBank = isWotPlusEnabled and (hasWotPlusActive or isWotPlusNSEnabled or hasGold)
    if showNewPiggyBank:
        from gui.impl.lobby.currency_reserves.currency_reserves_view import CurrencyReservesView
        viewId = R.views.lobby.currency_reserves.CurrencyReserves()
        params = GuiImplViewLoadParams(viewId, CurrencyReservesView, ScopeTemplates.LOBBY_SUB_SCOPE)
    else:
        from gui.impl.lobby.premacc.piggybank import PiggyBankView
        viewId = R.views.lobby.premacc.piggybank.Piggybank()
        params = GuiImplViewLoadParams(viewId, PiggyBankView, ScopeTemplates.LOBBY_SUB_SCOPE)
    uiLoader = dependency.instance(IGuiLoader)
    dtView = uiLoader.windowsManager.getViewByLayoutID(viewId)
    if dtView is not None:
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(params), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showMapsBlacklistView():
    from gui.impl.lobby.premacc.maps_blacklist_view import MapsBlacklistView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=R.views.lobby.premacc.maps_blacklist_view.MapsBlacklistView(), viewClass=MapsBlacklistView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showDailyExpPageView(exitEvent=None):
    from gui.impl.lobby.premacc.daily_experience_view import DailyExperienceView
    exitEvent = exitEvent or events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR))
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=R.views.lobby.premacc.daily_experience_view.DailyExperiencePage(), viewClass=DailyExperienceView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'exitEvent': exitEvent}), scope=EVENT_BUS_SCOPE.LOBBY)


def showDashboardView():
    from gui.impl.lobby.premacc.prem_dashboard_view import PremDashboardView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.premacc.prem_dashboard_view.PremDashboardView(), PremDashboardView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


@async
def showBattleBoosterBuyDialog(battleBoosterIntCD):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.lobby.instructions.booster_buy_dialog import BoosterBuyWindowView
    wrapper = FullScreenDialogWindowWrapper(BoosterBuyWindowView(battleBoosterIntCD))
    yield dialogs.showSimple(wrapper)


@async
def showBattleBoosterSellDialog(battleBoosterIntCD):
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.lobby.instructions.booster_sell_dialog import BoosterSellWindowView
    from gui.impl.dialogs import dialogs
    wrapper = FullScreenDialogWindowWrapper(BoosterSellWindowView(battleBoosterIntCD))
    yield dialogs.showSimple(wrapper)


@async
def showPlatoonResourceDialog(resources, callback):
    app = dependency.instance(IAppLoader).getApp()
    parent = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY)) if app is not None else None
    result = yield await(showResSimpleDialog(resources, None, '', parent))
    if result:
        callback(result)
    return


def showResearchView(vehTypeCompDescr, exitEvent=None):
    exitEvent = exitEvent or events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR))
    loadEvent = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_RESEARCH), ctx={'rootCD': vehTypeCompDescr,
     'exit': exitEvent})
    g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def showTechTree(vehTypeCompDescr=None, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(vehTypeCompDescr)
    nation = vehicle.nationName
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_TECHTREE), ctx={'nation': nation}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleStats(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PROFILE), ctx={'itemCD': vehTypeCompDescr}), scope=EVENT_BUS_SCOPE.LOBBY)


def showHangar():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)


def showBarracks():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_BARRACKS)), scope=EVENT_BUS_SCOPE.LOBBY)


def showBadges(backViewName=''):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BADGES_PAGE), ctx={'backViewName': backViewName} if backViewName else None), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showDogTags(compID=-1, makeTopView=True):
    lobbyContext = dependency.instance(ILobbyContext)
    if not lobbyContext.getServerSettings().isDogTagCustomizationScreenEnabled():
        return
    else:
        from gui.impl.lobby.dog_tags.dog_tags_view import DogTagsView
        uiLoader = dependency.instance(IGuiLoader)
        contentResId = R.views.lobby.dog_tags.DogTagsView()
        dtView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
        if dtView is not None:
            dtView.highlightComponent(compID)
        else:
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, DogTagsView, ScopeTemplates.LOBBY_SUB_SCOPE), highlightedComponentId=compID, makeTopView=makeTopView), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showStrongholds(url=None):
    strongholdProvider = g_clanCache.strongholdProvider
    browserCtrl = dependency.instance(IBrowserController)
    browserIsActive = browserCtrl is not None and browserCtrl.getAllBrowsers()
    if browserIsActive and strongholdProvider is not None and strongholdProvider.isTabActive():
        strongholdProvider.loadUrl(url)
    else:
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STRONGHOLD), ctx={'url': url}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def openManualPage(chapterIndex):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MANUAL_CHAPTER_VIEW), ctx={'chapterIndex': chapterIndex}), EVENT_BUS_SCOPE.LOBBY)


@adisp.process
def showShop(url='', path='', params=None, isClientCloseControl=False):
    parse = URLMacros().parse
    if path:
        path = yield parse(path, params)
        if url:
            url = yield parse(url)
        else:
            url = getShopURL()
    else:
        path = ''
        if url:
            url = yield parse(url, params)
        else:
            url = getShopURL()
    url = '/'.join((node.strip('/') for node in (url, path) if node))
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    if app is not None and app.containerManager is not None:
        viewKey = ViewKey(VIEW_ALIAS.LOBBY_STORE)
        browserWindow = app.containerManager.getViewByKey(viewKey)
        if browserWindow is not None:
            browser = browserWindow.getBrowser()
            browser.navigate(url)
            return
    ctx = {'url': url}
    if isClientCloseControl:
        ctx.update(getClientControlledCloseCtx())
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STORE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showStorage(defaultSection=STORAGE_CONSTANTS.FOR_SELL, tabId=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STORAGE), ctx={'defaultSection': defaultSection,
     'defaultTab': tabId}), scope=EVENT_BUS_SCOPE.LOBBY)


def showInterludeVideoWindow(messageVO=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_INTERLUDE_VIDEO), ctx=messageVO), EVENT_BUS_SCOPE.LOBBY)


def showSubtitleWindow(messageVO=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.SUBTITLES_WINDOW), ctx=messageVO), EVENT_BUS_SCOPE.LOBBY)


def showOldVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'vehicleStrCD': vehStrCD,
     'previewBackCb': previewBackCb}), scope=EVENT_BUS_SCOPE.LOBBY)


def showMarathonVehiclePreview(vehTypeCompDescr, itemsPack=None, title='', marathonPrefix='', backToHangar=False):
    previewAppearance = None
    if backToHangar:
        previewAppearance = HeroTankPreviewAppearance()
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'itemsPack': itemsPack,
     'title': title,
     'marathonPrefix': marathonPrefix,
     'previewAppearance': previewAppearance,
     'backToHangar': backToHangar}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showConfigurableVehiclePreview(vehTypeCompDescr, previewAlias, previewBackCb, hiddenBlocks, itemPack):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewBackCb': previewBackCb,
     'hiddenBlocks': hiddenBlocks,
     'itemsPack': itemPack}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None, itemsPack=None, offers=None, price=MONEY_UNDEFINED, oldPrice=None, title='', description=None, endTime=None, buyParams=None, vehParams=None):
    heroTankController = dependency.instance(IHeroTankController)
    heroTankCD = heroTankController.getCurrentTankCD()
    isHeroTank = heroTankCD and heroTankCD == vehTypeCompDescr
    if isHeroTank and not (itemsPack or offers or vehParams):
        goToHeroTankOnScene(vehTypeCompDescr, previewAlias, previewBackCb=previewBackCb)
    else:
        vehicle = dependency.instance(IItemsCache).items.getItemByCD(vehTypeCompDescr)
        if not (itemsPack or offers or vehParams) and vehicle.canPersonalTradeInBuy:
            viewAlias = VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW
        elif not (itemsPack or offers or vehParams) and vehicle.canTradeIn:
            viewAlias = VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW
        elif offers and offers[0].eventType == 'subscription':
            viewAlias = VIEW_ALIAS.WOT_PLUS_VEHICLE_PREVIEW
        elif offers and offers[0].eventType == 'telecom_rentals':
            viewAlias = VIEW_ALIAS.WOT_PLUS_VEHICLE_PREVIEW
        else:
            viewAlias = VIEW_ALIAS.VEHICLE_PREVIEW
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(viewAlias), ctx={'itemCD': vehTypeCompDescr,
         'previewAlias': previewAlias,
         'vehicleStrCD': vehStrCD,
         'previewBackCb': previewBackCb,
         'itemsPack': itemsPack,
         'offers': offers,
         'price': price,
         'oldPrice': oldPrice,
         'title': title,
         'description': description,
         'endTime': endTime,
         'buyParams': buyParams,
         'vehParams': vehParams}), scope=EVENT_BUS_SCOPE.LOBBY)


def goToHeroTankOnScene(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previewBackCb=None, previousBackAlias=None, hangarVehicleCD=None):
    import BigWorld
    from HeroTank import HeroTank
    from ClientSelectableCameraObject import ClientSelectableCameraObject
    marathonCtrl = dependency.instance(IMarathonEventsController)
    for entity in BigWorld.entities.values():
        if entity and isinstance(entity, HeroTank):
            descriptor = entity.typeDescriptor
            if descriptor:
                marathons = marathonCtrl.getMarathons()
                activeMarathon = next((marathon for marathon in marathons if marathon.vehicleID == descriptor.type.compactDescr), None)
                if activeMarathon:
                    title = backport.text(R.strings.marathon.vehiclePreview.buyingPanel.title())
                    showMarathonVehiclePreview(descriptor.type.compactDescr, activeMarathon.remainingPackedRewards, title, activeMarathon.prefix, True)
                else:
                    showHeroTankPreview(vehTypeCompDescr, previewAlias=previewAlias, previewBackCb=previewBackCb, previousBackAlias=previousBackAlias, hangarVehicleCD=hangarVehicleCD)
            ClientSelectableCameraObject.switchCamera(entity)
            break

    return


def showHeroTankPreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previousBackAlias=None, previewBackCb=None, hangarVehicleCD=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.HERO_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True,
     'previousBackAlias': previousBackAlias,
     'previewBackCb': previewBackCb,
     'hangarVehicleCD': hangarVehicleCD}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideVehiclePreview(back=True, close=False):
    ctx = {'back': back,
     'close': close}
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_VEHICLE_PREVIEW, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def hideBattleResults():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)


def hideSquadWindow():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_UNIT_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)


def hideWebBrowser(browserID=None):
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_BROWSER_WINDOW, ctx={'browserID': browserID}), scope=EVENT_BUS_SCOPE.LOBBY)


def hideWebBrowserOverlay():
    g_eventBus.handleEvent(events.HideWindowEvent(events.HideWindowEvent.HIDE_OVERLAY_BROWSER_VIEW), scope=EVENT_BUS_SCOPE.LOBBY)


def showAwardWindow(award, isUniqueName=True):
    if isPopupsWindowsOpenDisabled():
        LOG_WARNING('Award popup disabled', award, isUniqueName)
        return
    if isUniqueName:
        name = getUniqueViewName(VIEW_ALIAS.AWARD_WINDOW)
    else:
        name = VIEW_ALIAS.AWARD_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.AWARD_WINDOW, name), ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


def showModalAwardWindow(award):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.AWARD_WINDOW_MODAL, name=getUniqueViewName(VIEW_ALIAS.AWARD_WINDOW_MODAL)), ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


def showMissionAwardWindow(award):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MISSION_AWARD_WINDOW, name=getUniqueViewName(VIEW_ALIAS.MISSION_AWARD_WINDOW)), ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showPersonalMissionsQuestAwardScreen(quest, ctx, proxyEvent, notificationMgr=None):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_QUEST_AWARD_SCREEN_ALIAS
    window = SFWindow(SFViewLoadParams(alias, getUniqueViewName(alias)), ctx={'quest': quest,
     'ctxData': ctx,
     'proxyEvent': proxyEvent}, scope=EVENT_BUS_SCOPE.LOBBY)
    notificationMgr.append(WindowNotificationCommand(window))


def showProfileWindow(databaseID, userName):
    alias = VIEW_ALIAS.PROFILE_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, getViewName(alias, databaseID)), ctx={'userName': userName,
     'databaseID': databaseID}), EVENT_BUS_SCOPE.LOBBY)


def showClanProfileWindow(clanDbID, clanAbbrev):
    alias = CLANS_ALIASES.CLAN_PROFILE_MAIN_WINDOW_PY
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, getViewName(alias, clanDbID)), ctx={'clanDbID': clanDbID,
     'clanAbbrev': clanAbbrev}), EVENT_BUS_SCOPE.LOBBY)


def showClanSearchWindow():
    alias = CLANS_ALIASES.CLAN_SEARCH_WINDOW_PY
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, alias), ctx=None), EVENT_BUS_SCOPE.LOBBY)
    return


def showClanInvitesWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(CLANS_ALIASES.CLAN_PROFILE_INVITES_WINDOW_PY)), EVENT_BUS_SCOPE.LOBBY)


def showClanPersonalInvitesWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(CLANS_ALIASES.CLAN_PERSONAL_INVITES_WINDOW_PY)), EVENT_BUS_SCOPE.LOBBY)


def showClanSendInviteWindow(clanDbID):
    alias = CLANS_ALIASES.CLAN_PROFILE_SEND_INVITES_WINDOW_PY
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, getViewName(alias, clanDbID)), ctx={'clanDbID': clanDbID,
     'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)


def selectVehicleInHangar(itemCD, loadHangar=True):
    from CurrentVehicle import g_currentVehicle
    itemsCache = dependency.instance(IItemsCache)
    veh = itemsCache.items.getItemByCD(int(itemCD))
    if not veh.isInInventory:
        raise SoftException('Vehicle (itemCD={}) must be in inventory.'.format(itemCD))
    g_currentVehicle.selectVehicle(veh.invID)
    if loadHangar:
        showHangar()


def showPersonalCase(tankmanInvID, tabIndex, scope=EVENT_BUS_SCOPE.DEFAULT):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.PERSONAL_CASE, getViewName(VIEW_ALIAS.PERSONAL_CASE, tankmanInvID)), ctx={'tankmanID': tankmanInvID,
     'page': tabIndex}), scope)


def showCollectibleVehicles(nationID):
    nationName = NAMES[nationID]
    showShop(getBuyCollectibleVehiclesUrl(), nationName)


@adisp.async
@adisp.process
@dependency.replace_none_kwargs(goodiesCache=IGoodiesCache)
def showBoosterActivateDialog(boosterIntCD, callback=None, goodiesCache=None):
    success = False
    newBooster = goodiesCache.getBooster(boosterIntCD)
    if newBooster.isReadyToActivate:
        criteria = REQ_CRITERIA.BOOSTER.ACTIVE | REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([newBooster.boosterType])
        activeBoosters = goodiesCache.getBoosters(criteria=criteria).values()
        curBooster = max(activeBoosters, key=attrgetter('effectValue')) if activeBoosters else None
        messageCtx = {'newBoosterName': text_styles.middleTitle(newBooster.description)}
        if curBooster is None:
            key = BOOSTER_CONSTANTS.BOOSTER_ACTIVATION_CONFORMATION_TEXT_KEY
        else:
            key = BOOSTER_CONSTANTS.BOOSTER_REPLACE_CONFORMATION_TEXT_KEY
            messageCtx['curBoosterName'] = text_styles.middleTitle(curBooster.description)
        shouldActivate = yield DialogsInterface.showDialog(I18nConfirmDialogMeta(key=key, messageCtx=messageCtx, focusedID=DIALOG_BUTTON_ID.CLOSE))
        if shouldActivate:
            result = yield BoosterActivator(newBooster).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            success = result.success
    if callback is not None:
        callback(success)
    return


def stopTutorial():
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.STOP_TRAINING), scope=EVENT_BUS_SCOPE.GLOBAL)


def runTutorialChain(chapterID):
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.START_TRAINING, settingsID='TRIGGERS_CHAINS', initialChapter=chapterID, restoreIfRun=True))


def runSalesChain(chapterID, restoreIfRun=True, reloadIfRun=False, isStopForced=False):
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.START_TRAINING, settingsID='SALES_TRIGGERS', initialChapter=chapterID, restoreIfRun=restoreIfRun, reloadIfRun=reloadIfRun, isStopForced=isStopForced))


def changeAppResolution(width, height, scale):
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.CHANGE_APP_RESOLUTION, ctx={'width': width,
     'height': height,
     'scale': scale}), scope=EVENT_BUS_SCOPE.GLOBAL)


@adisp.process
def requestProfile(databaseID, userName, successCallback):
    itemsCache = dependency.instance(IItemsCache)
    userDossier, _, isHidden = yield itemsCache.items.requestUserDossier(databaseID)
    if userDossier is None:
        if isHidden:
            key = 'messenger/userInfoHidden'
        else:
            key = 'messenger/userInfoNotAvailable'
        DialogsInterface.showI18nInfoDialog(key, lambda result: None, I18nInfoDialogMeta(key, messageCtx={'userName': userName}))
    else:
        successCallback(databaseID, userName)
    return


def showSettingsWindow(redefinedKeyMode=False, tabIndex=None, isBattleSettings=False):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.SETTINGS_WINDOW), ctx={'redefinedKeyMode': redefinedKeyMode,
     'tabIndex': tabIndex,
     'isBattleSettings': isBattleSettings}), scope=EVENT_BUS_SCOPE.GLOBAL)


def showVehicleCompare():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEHICLE_COMPARE)), scope=EVENT_BUS_SCOPE.LOBBY)


@pointcutable
def showCrystalWindow(visibility):
    from gui.impl.lobby.crystals_promo.crystals_promo_view import CrystalsPromoView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.crystalsPromo.CrystalsPromoView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, CrystalsPromoView, ScopeTemplates.LOBBY_SUB_SCOPE), visibility=visibility), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@pointcutable
def openPaymentLink():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PAYMENT))


@pointcutable
def showExchangeCurrencyWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EXCHANGE_WINDOW)), EVENT_BUS_SCOPE.LOBBY)


@pointcutable
def showExchangeXPWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EXCHANGE_XP_WINDOW)), EVENT_BUS_SCOPE.LOBBY)


def showBubbleTooltip(msg):
    g_eventBus.handleEvent(events.BubbleTooltipEvent(events.BubbleTooltipEvent.SHOW, msg), scope=EVENT_BUS_SCOPE.LOBBY)


def showReferralProgramWindow(url=None):
    referralController = dependency.instance(IReferralProgramController)
    if url is None:
        url = getReferralProgramURL()
    referralController.showWindow(url=url)
    return


def showClanQuestWindow(url=None):
    clanNotificationController = dependency.instance(IClanNotificationController)
    if url is None:
        url = getClanQuestURL()
    clanNotificationController.showWindow(url=url)
    return


def showTankPremiumAboutPage():
    url = GUI_SETTINGS.premiumInfo.get('baseURL')
    if url is None:
        _logger.error('premiumInfo.baseURL is missed')
    showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)
    return


@adisp.process
def showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, params=None, callbackOnLoad=None, webHandlers=None, forcedSkipEscape=False, browserParams=None, hiddenLayers=None):
    if url:
        if browserParams is None:
            browserParams = {}
        url = yield URLMacros().parse(url, params=params)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias), ctx={'url': url,
         'allowRightClick': False,
         'callbackOnLoad': callbackOnLoad,
         'webHandlers': webHandlers,
         'forcedSkipEscape': forcedSkipEscape,
         'browserParams': browserParams,
         'hiddenLayers': hiddenLayers or ()}), EVENT_BUS_SCOPE.LOBBY)
    return


def showProgressiveRewardWindow():
    lobbyContext = dependency.instance(ILobbyContext)
    if not lobbyContext.getServerSettings().getProgressiveRewardConfig().isEnabled:
        SystemMessages.pushMessage(backport.text(R.strings.system_messages.progressiveReward.error()), type=SystemMessages.SM_TYPE.Error)
        return
    else:
        from gui.impl.lobby.progressive_reward.progressive_reward_view import ProgressiveRewardWindow
        uiLoader = dependency.instance(IGuiLoader)
        contentResId = R.views.lobby.progressive_reward.progressive_reward_view.ProgressiveRewardView()
        if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
            window = ProgressiveRewardWindow(contentResId)
            window.load()
        return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showProgressiveRewardAwardWindow(bonuses, specialRewardType, currentStep, notificationMgr=None):
    from gui.impl.lobby.progressive_reward.progressive_reward_award_view import ProgressiveRewardAwardWindow
    window = ProgressiveRewardAwardWindow(bonuses, specialRewardType, currentStep)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showSeniorityRewardAwardWindow(qID, data, notificationMgr=None):
    from gui.impl.lobby.seniority_awards.seniority_reward_award_view import SeniorityRewardAwardWindow
    from account_helpers.AccountSettings import AccountSettings, SENIORITY_AWARDS_WINDOW_SHOWN
    AccountSettings.setSessionSettings(SENIORITY_AWARDS_WINDOW_SHOWN, True)
    window = SeniorityRewardAwardWindow(qID, data, R.views.lobby.seniority_awards.SeniorityAwardsView())
    notificationMgr.append(WindowNotificationCommand(window))


def showSeniorityAwardsNotificationWindow():
    from gui.impl.lobby.seniority_awards.seniority_awards_notification_view import SeniorityAwardsNotificationWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.seniority_awards.SeniorityAwardsNotificationView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        window = SeniorityAwardsNotificationWindow()
        window.load()
        window.center()
    return


def showBattlePassAwardsWindow(bonuses, data, useQueue=False):
    from gui.impl.lobby.battle_pass.battle_pass_awards_view import BattlePassAwardWindow
    findAndLoadWindow(useQueue, BattlePassAwardWindow, bonuses, data)


def showBattlePassHowToEarnPointsView(parent=None, chapterID=0):
    from gui.impl.lobby.battle_pass.battle_pass_how_to_earn_points_view import BattlePassHowToEarnPointsWindow
    window = BattlePassHowToEarnPointsWindow(parent=parent if parent is not None else getParentWindow(), chapterID=chapterID)
    window.load()
    return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showBattlePassVehicleAwardWindow(data, notificationMgr=None):
    from gui.impl.lobby.battle_pass.battle_pass_vehicle_award_view import BattlePassVehicleAwardWindow
    window = BattlePassVehicleAwardWindow(data)
    notificationMgr.append(WindowNotificationCommand(window))


def showDedicationRewardWindow(bonuses, data, closeCallback=None):
    from gui.impl.lobby.dedication.dedication_reward_view import DedicationRewardWindow
    window = DedicationRewardWindow(bonuses, data, closeCallback)
    window.load()


def isViewLoaded(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    if not uiLoader or not uiLoader.windowsManager:
        return False
    else:
        view = uiLoader.windowsManager.getViewByLayoutID(layoutID)
        return view is not None


def showStylePreview(vehCD, style, descr, backCallback, backBtnDescrLabel='', *args, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STYLE_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': descr,
     'backCallback': backCallback,
     'backBtnDescrLabel': backBtnDescrLabel}), scope=EVENT_BUS_SCOPE.LOBBY)


def showStyleProgressionPreview(vehCD, style, descr, backCallback, backBtnDescrLabel='', *args, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': descr,
     'backCallback': backCallback,
     'backBtnDescrLabel': backBtnDescrLabel,
     'styleLevel': kwargs.get('styleLevel')}), scope=EVENT_BUS_SCOPE.LOBBY)


def showBattlePassStyleProgressionPreview(vehCD, style, descr, backCallback, backBtnDescrLabel='', *args, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': descr,
     'backCallback': backCallback,
     'backBtnDescrLabel': backBtnDescrLabel,
     'styleLevel': kwargs.get('styleLevel'),
     'chapterId': kwargs.get('chapterId')}), scope=EVENT_BUS_SCOPE.LOBBY)


def showStyleBuyingPreview(vehCD, style, descr, backCallback, backBtnDescrLabel='', *args, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STYLE_BUYING_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': descr,
     'backCallback': backCallback,
     'backBtnDescrLabel': backBtnDescrLabel,
     'styleLevel': kwargs.get('styleLevel'),
     'price': kwargs.get('price'),
     'buyParams': kwargs.get('buyParams')}), scope=EVENT_BUS_SCOPE.LOBBY)


def showRankedSeasonCompleteView(ctx, useQueue=False):
    params = SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE)
    findAndLoadWindow(useQueue, SFWindow, params, EVENT_BUS_SCOPE.LOBBY, ctx=ctx)


def showRankedYearAwardWindow(rawAwards, points, useQueue=False, showRemainedSelection=False):
    from gui.impl.lobby.ranked.ranked_year_award_view import RankedYearAwardWindow
    findAndLoadWindow(useQueue, RankedYearAwardWindow, rawAwards, points, showRemainedSelection)


def showRankedYearLBAwardWindow(playerPosition, rewardsData, useQueue=False):
    from gui.impl.lobby.ranked.year_leaderboard_view import YearLeaderboardAwardWindow
    findAndLoadWindow(useQueue, YearLeaderboardAwardWindow, playerPosition, rewardsData)


def findAndLoadWindow(useQueue, windowType, *args, **kwargs):
    guiLoader = dependency.instance(IGuiLoader)
    notificationMgr = dependency.instance(INotificationWindowController)

    def windowsFilter(window):
        return isinstance(window, windowType) and window.windowStatus not in (WindowStatus.DESTROYING, WindowStatus.DESTROYED) and window.isParamsEqual(*args, **kwargs)

    windows = guiLoader.windowsManager.findWindows(windowsFilter)
    for w in windows:
        if not useQueue and w.windowStatus == WindowStatus.CREATED:
            w.load()
        return w

    newWindow = windowType(*args, **kwargs)
    if useQueue:
        notificationMgr.append(WindowNotificationCommand(newWindow))
    else:
        newWindow.load()
    return newWindow


@async
def showPreformattedDialog(preset, title, message, buttons, focusedButton, btnDownSounds):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import FormattedSimpleDialogBuilder
    builder = FormattedSimpleDialogBuilder()
    builder.setMessagesAndButtons(preset, title, message, buttons, focusedButton, btnDownSounds)
    result = yield await(dialogs.show(builder.build()))
    raise AsyncReturn(result)


@async
def showResSimpleDialog(resources, icon, formattedMessage, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import ResSimpleDialogBuilder
    builder = ResSimpleDialogBuilder()
    builder.setMessagesAndButtons(resources)
    builder.setIcon(icon)
    builder.setFormattedMessage(formattedMessage)
    result = yield await(dialogs.showSimple(builder.build(parent)))
    raise AsyncReturn(result)


@async
def showDynamicButtonInfoDialogBuilder(resources, icon, formattedMessage, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import InfoDialogBuilder
    builder = InfoDialogBuilder()
    builder.setMessagesAndButtons(resources, resources)
    builder.setIcon(icon)
    builder.setFormattedMessage(formattedMessage)
    result = yield await(dialogs.showSimple(builder.build(parent)))
    raise AsyncReturn(result)


@async
def tryToShowReplaceExistingStyleDialog(parent=None):
    from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import WarningDialogBuilder
    from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.shared.gui_items import GUI_ITEM_TYPE
    from skeletons.account_helpers.settings_core import ISettingsCore
    from skeletons.gui.customization import ICustomizationService
    from items.components.c11n_constants import EDITABLE_STYLE_STORAGE_DEPTH
    from CurrentVehicle import g_currentVehicle
    from items.customizations import isEditedStyle
    from items.components.c11n_constants import SeasonType
    from gui.Scaleform.daapi.view.lobby.customization.shared import fitOutfit, getCurrentVehicleAvailableRegionsMap, getEditableStyleOutfitDiffComponent
    service = dependency.instance(ICustomizationService)
    settingsCore = dependency.instance(ISettingsCore)
    serverSettings = settingsCore.serverSettings
    if serverSettings.getUIStorage().get(UI_STORAGE_KEYS.DISABLE_EDITABLE_STYLE_REWRITE_WARNING):
        raise AsyncReturn(True)
    context = service.getCtx()
    currentStyle = context.mode.currentOutfit.style
    if currentStyle is None:
        raise AsyncReturn(True)
    if not currentStyle.isEditable:
        raise AsyncReturn(True)
    vehicleCD = g_currentVehicle.item.descriptor.makeCompactDescr()
    baseStyle = service.getItemByID(GUI_ITEM_TYPE.STYLE, currentStyle.id)
    availableRegionsMap = getCurrentVehicleAvailableRegionsMap()
    for season in SeasonType.COMMON_SEASONS:
        outfit = context.mode.getModifiedOutfit(season)
        baseOutfit = baseStyle.getOutfit(season, vehicleCD=vehicleCD)
        fitOutfit(baseOutfit, availableRegionsMap)
        diff = getEditableStyleOutfitDiffComponent(outfit, baseOutfit)
        if isEditedStyle(diff):
            break
    else:
        raise AsyncReturn(True)

    storedStyleDiffs = service.getStoredStyleDiffs()
    for diff in storedStyleDiffs:
        if currentStyle.id == diff[0]:
            raise AsyncReturn(True)

    if len(storedStyleDiffs) < EDITABLE_STYLE_STORAGE_DEPTH:
        raise AsyncReturn(True)
    newStyleName = currentStyle.userString
    styleToReplaceName = service.getItemByID(GUI_ITEM_TYPE.STYLE, storedStyleDiffs[-1][0]).userName
    context.mode.unselectSlot()
    builder = WarningDialogBuilder()
    builder.setTitleArgs([newStyleName])
    builder.setMessageArgs(fmtArgs=[UserFormatStringArgModel('{} {}'.format(styleToReplaceName, backport.text(R.strings.dialogs.editableStyles.confirmReset.formattedPartOfMessage())), 'formatted_message', R.styles.AlertBigTextStyle())])
    builder.setMessagesAndButtons(R.strings.dialogs.editableStyles.confirmReset, focused=DialogButtons.CANCEL)
    result, dontShowAgain = yield await(dialogs.showSimpleWithResultData(builder.build(parent=parent)))
    if result and dontShowAgain:
        serverSettings.saveInUIStorage({UI_STORAGE_KEYS.DISABLE_EDITABLE_STYLE_REWRITE_WARNING: True})
    raise AsyncReturn(result)
    return


@async
def showDialog(dialog, callback):
    from gui.impl.dialogs import dialogs
    isOk = yield await(dialogs.showSimple(dialog))
    callback((isOk, {}))


@async
def showOptDeviceCommonWindowDialog(wrappedViewClass, deviceDescr=None, layoutID=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(compDescr=deviceDescr, layoutID=layoutID or R.views.lobby.demountkit.CommonWindow(), wrappedViewClass=wrappedViewClass))
    if result.busy:
        raise AsyncReturn((False, {}))
    else:
        isOk, _ = result.result
        raise AsyncReturn((isOk, {}))


@async
def showOptionalDeviceDestroy(itemCD, callback):
    from gui.impl.dialogs.gf_builders import WarningDialogBuilder
    builder = WarningDialogBuilder()
    builder.setConfirmButtonLabel(R.strings.dialogs.removeConfirmationNotRemovable.submit())
    optionalDevice = dependency.instance(IItemsCache).items.getItemByCD(itemCD)
    title = backport.text(R.strings.dialogs.equipmentDestroy.conformation(), equipment=optionalDevice.userName)
    builder.setTitle(title)
    from gui.impl.dialogs.dialog_template import DialogTemplateView
    result = yield await(showOptDeviceCommonWindowDialog(lambda **_: builder.buildView(), layoutID=DialogTemplateView.LAYOUT_ID))
    callback(result)


@async
def showOptionalDeviceDemount(deviceDescr, callback, forFitting=False):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.demount_kit.demount_dialog import DemountOptionalDeviceDialog
    result = yield await(dialogs.showSingleDialogWithResultData(itemCD=deviceDescr, forFitting=forFitting, layoutID=DemountOptionalDeviceDialog.LAYOUT_ID, wrappedViewClass=DemountOptionalDeviceDialog))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        if data.get('openSingleDemountWindow', False):
            showOptionalDeviceDemountSinglePrice(deviceDescr, callback, forFitting=forFitting)
        else:
            callback((isOK, data))


@async
def showOptionalDeviceDemountSinglePrice(deviceDescr, callback, forFitting=False):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.demount_kit.demount_single_price_dialog import DemountOptionalDeviceSinglePriceDialog
    result = yield await(dialogs.showSingleDialogWithResultData(itemCD=deviceDescr, forFitting=forFitting, layoutID=DemountOptionalDeviceSinglePriceDialog.LAYOUT_ID, wrappedViewClass=DemountOptionalDeviceSinglePriceDialog))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        if data.get('openDemountSelectorWindow', False):
            showOptionalDeviceDemount(deviceDescr, callback, forFitting=forFitting)
        else:
            callback((isOK, data))


@async
def showOptionalDeviceDemountFromSlot(deviceDescr, callback, forFitting=False, vehicle=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.demount_kit.demount_from_slot_dialog import DemountOptionalDeviceFromSlotDialog
    result = yield await(dialogs.showSingleDialogWithResultData(itemCD=deviceDescr, forFitting=forFitting, vehicle=vehicle, layoutID=DemountOptionalDeviceFromSlotDialog.LAYOUT_ID, wrappedViewClass=DemountOptionalDeviceFromSlotDialog))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


def _killOldView(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    if not uiLoader or not uiLoader.windowsManager:
        return
    view = uiLoader.windowsManager.getViewByLayoutID(layoutID)
    if view:
        view.destroyWindow()
        return True
    return False


def showOfferGiftsWindow(offerID, overrideSuccessCallback=None):
    from gui.impl.lobby.offers.offer_gifts_window import OfferGiftsWindow
    layoutID = R.views.lobby.offers.OfferGiftsWindow()
    _killOldView(layoutID)
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, OfferGiftsWindow, ScopeTemplates.LOBBY_SUB_SCOPE), offerID=offerID, overrideSuccessCallback=overrideSuccessCallback), scope=EVENT_BUS_SCOPE.LOBBY)


@async
def showOfferGiftDialog(offerID, giftID, cdnTitle='', callback=None):
    from gui.impl.lobby.offers.offer_gift_dialog import makeOfferGiftDialog
    dialogBuilder = makeOfferGiftDialog(offerID, giftID, cdnTitle)
    app = dependency.instance(IAppLoader).getApp()
    view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
    yield showDialog(dialogBuilder.build(parent=view), callback)


def showOfferGiftVehiclePreview(offerID, giftID, confirmCallback=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW), ctx={'offerID': offerID,
     'giftID': giftID,
     'confirmCallback': confirmCallback}), scope=EVENT_BUS_SCOPE.LOBBY)


def showOfferRewardWindow(offerID, giftID, cdnTitle='', cdnDescription='', cdnIcon=''):
    from gui.impl.lobby.offers.offer_reward_window import OfferRewardWindow
    window = LobbyWindow(content=OfferRewardWindow(R.views.lobby.offers.OfferRewardWindow(), offerID=offerID, giftID=giftID, cdnTitle=cdnTitle, cdnDescription=cdnDescription, cdnIcon=cdnIcon), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)
    window.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showProgressiveItemsRewardWindow(itemCD, vehicleCD, progressionLevel, showSecondButton=True, notificationMgr=None):
    from gui.impl.lobby.customization.progressive_items_reward.progressive_items_upgrade_view import ProgressiveItemsUpgradeWindow
    window = ProgressiveItemsUpgradeWindow(itemCD, vehicleCD, progressionLevel, showSecondButton)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showProgressionRequiredStyleUnlockedWindow(vehicleCD, notificationMgr=None):
    from gui.impl.lobby.customization.style_unlocked_view.style_unlocked_view import StyleUnlockedWindow
    window = StyleUnlockedWindow(vehicleCD)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showBadgeInvoiceAwardWindow(badge, notificationMgr=None):
    from gui.impl.lobby.awards.badge_award_view import BadgeAwardViewWindow
    window = BadgeAwardViewWindow(badge)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showMultiAwardWindow(rewards, tTips, productCode, notificationMgr=None):
    from gui.impl.lobby.awards.multiple_awards_view import MultipleAwardsViewWindow
    window = MultipleAwardsViewWindow(rewards, tTips, productCode)
    notificationMgr.append(WindowNotificationCommand(window))


def showProgressiveItemsView(itemIntCD=None):
    from gui.impl.lobby.customization.progressive_items_view.progressive_items_view import ProgressiveItemsView
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION))
    if view is None:
        parent = None
        _logger.error('ProgressiveItemsView shall be created only from customization')
    else:
        parent = view.getParentWindow()
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.customization.progressive_items_view.ProgressiveItemsView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=ProgressiveItemsView, scope=ScopeTemplates.LOBBY_SUB_SCOPE, parent=parent), view, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, itemIntCD=itemIntCD), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showAmmunitionSetupView(**kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.AMMUNITION_SETUP_VIEW), ctx=kwargs), scope=EVENT_BUS_SCOPE.LOBBY)


def showCompareAmmunitionSelectorView(**kwargs):
    from gui.impl.lobby.vehicle_compare.ammunition_selector import CompareAmmunitionSelectorView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.tanksetup.VehicleCompareAmmunitionSetup()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=CompareAmmunitionSelectorView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, ctx=kwargs), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@async
def showNeedRepairDialog(vehicle, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.NeedRepair(), wrappedViewClass=NeedRepair, vehicle=vehicle, startState=startState, parent=parent))
    raise AsyncReturn(result)


@async
def showTankSetupConfirmDialog(items, vehicle=None, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=TankSetupConfirmDialog, items=items, vehicle=vehicle, startState=startState, parent=parent))
    raise AsyncReturn(result)


@async
def showTankSetupExitConfirmDialog(items, vehicle=None, startState=None, fromSection=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=TankSetupExitConfirmDialog, items=items, vehicle=vehicle, startState=startState, fromSection=fromSection, parent=parent))
    raise AsyncReturn(result)


@async
def showRefillShellsDialog(price, shells, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.RefillShells(), wrappedViewClass=RefillShells, price=price, shells=shells, startState=startState, parent=parent))
    raise AsyncReturn(result)


@async
def showExitFromShellsDialog(price, shells, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.RefillShells(), wrappedViewClass=ExitFromShellsConfirm, price=price, shells=shells, startState=startState, parent=parent))
    raise AsyncReturn(result)


@async
def showBattleAbilitiesConfirmDialog(items, withInstall=None, parent=None):
    from gui.impl.lobby.tank_setup.dialogs.battle_abilities_confirm import BattleAbilitiesSetupConfirm
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=BattleAbilitiesSetupConfirm, items=items, withInstall=withInstall, parent=parent))
    raise AsyncReturn(result)


def showBlueprintsSalePage(url=None):
    showBlueprintsExchangeOverlay(url=url)


@async
def showActiveTestConfirmDialog(startTime, finishTime, link, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.matchmaker.active_test_confirm_view import ActiveTestConfirmView
    result = yield await(dialogs.showSingleDialog(layoutID=R.views.lobby.matchmaker.ActiveTestConfirmView(), wrappedViewClass=ActiveTestConfirmView, startTime=startTime, finishTime=finishTime, link=link, parent=parent))
    isOK = result.result
    raise AsyncReturn(isOK)


def showBattlePassDailyQuestsIntroWindow(parent=None):
    from gui.impl.lobby.battle_pass.battle_pass_daily_quests_intro_view import BattlePassDailyQuestsIntroWindow
    window = BattlePassDailyQuestsIntroWindow(parent=parent if parent is not None else getParentWindow())
    window.load()
    return


def showBattlePassRewardsSelectionWindow(chapterID=0, level=0, onRewardsReceivedCallback=None, onCloseCallback=None):
    from gui.impl.lobby.battle_pass.rewards_selection_view import RewardsSelectionWindow
    window = RewardsSelectionWindow(chapterID, level, onRewardsReceivedCallback, onCloseCallback)
    window.load()


@async
def showBattlePassActivateChapterConfirmDialog(chapterID, callback):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.battle_pass.activate_chapter_confirm_dialog import ActivateChapterConfirmDialog
    result = yield await(dialogs.showSingleDialogWithResultData(chapterID=chapterID, layoutID=ActivateChapterConfirmDialog.LAYOUT_ID, wrappedViewClass=ActivateChapterConfirmDialog))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showBattlePassBuyWindow(ctx=None, parent=None, guiLoader=None):
    from gui.impl.lobby.battle_pass.battle_pass_buy_view import BattlePassBuyWindow
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.BattlePassBuyView())
    if view is None:
        window = BattlePassBuyWindow(ctx or {}, parent or getParentWindow())
        window.load()
    return


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showBattlePassBuyLevelWindow(ctx=None, parent=None, guiLoader=None):
    from gui.impl.lobby.battle_pass.battle_pass_buy_levels_view import BattlePassBuyLevelWindow
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.BattlePassBuyView())
    if view is None:
        window = BattlePassBuyLevelWindow(ctx or {}, parent or getParentWindow())
        window.load()
    return


@async
def showVehPostProgressionView(vehTypeCompDescr, exitEvent=None):
    from gui.impl.lobby.veh_post_progression.post_progression_intro import getPostProgressionIntroWindowProc
    intoProc = getPostProgressionIntroWindowProc()
    yield intoProc.show()
    loadEvent = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEH_POST_PROGRESSION), ctx={'intCD': vehTypeCompDescr,
     'exit': exitEvent})
    g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)


def showVehPostProgressionCmpView(vehTypeCompDescr, exitEvent=None):
    loadEvent = events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEH_POST_PROGRESSION_CMP), ctx={'intCD': vehTypeCompDescr,
     'exit': exitEvent})
    g_eventBus.handleEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)
    VehPostProgressionEntryPointLogger().logEnter()


def getParentWindow():
    guiLoader = dependency.instance(IGuiLoader)
    windows = guiLoader.windowsManager.findWindows(lambda w: w.layer == WindowLayer.SUB_VIEW)
    return first(windows)


def showMapboxPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(MAPBOX_ALIASES.MAPBOX_PRIME_TIME), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showMapboxIntro(closeCallback=None):
    from gui.impl.lobby.mapbox.map_box_intro import MapBoxIntroWindow
    if not MapBoxIntroWindow.getInstances():
        window = MapBoxIntroWindow(closeCallback)
        window.load()


def showMapboxAward(numBattles, rewards):
    from gui.impl.lobby.mapbox.map_box_awards_view import MapBoxAwardsViewWindow
    if not MapBoxAwardsViewWindow.getInstances():
        MapBoxAwardsViewWindow(numBattles, rewards).load()


def showMapboxRewardChoice(selectableCrewbook):
    from gui.impl.lobby.mapbox.mapbox_reward_choice_view import MapboxRewardChoiceWindow
    if not MapboxRewardChoiceWindow.getInstances():
        MapboxRewardChoiceWindow(selectableCrewbook).load()


@waitShowOverlay
def showSteamAddEmailOverlay(initialEmail='', onClose=None):
    from gui.impl.lobby.account_completion.steam_add_email_overlay_view import SteamAddEmailOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(SteamAddEmailOverlayView, initialEmail=initialEmail, onClose=onClose)


@waitShowOverlay
def showDemoAddCredentialsOverlay(initialEmail='', emailError='', onClose=None):
    from gui.impl.lobby.account_completion.demo_add_credentials_overlay_view import DemoAddCredentialsOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(DemoAddCredentialsOverlayView, initialEmail=initialEmail, emailError=emailError, onClose=onClose)


@waitShowOverlay
def showSteamConfirmEmailOverlay(email='', onClose=None):
    from gui.impl.lobby.account_completion.steam_confirm_email_overlay_view import SteamConfirmEmailOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(SteamConfirmEmailOverlayView, email=email, onClose=onClose)


@waitShowOverlay
def showDemoRenamingUnavailableOverlay(onClose=None):
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    from gui.impl.lobby.account_completion.demo_renaming_unavailable_overlay_view import DemoRenamingUnavailableOverlayView
    wnd.setSubView(DemoRenamingUnavailableOverlayView, onClose=onClose)


@waitShowOverlay
def showDemoConfirmCredentialsOverlay(email='', onClose=None):
    from gui.impl.lobby.account_completion.demo_confirm_credentials_overlay_view import DemoConfirmCredentialsOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(DemoConfirmCredentialsOverlayView, email=email, onClose=onClose)


@waitShowOverlay
def showDemoWaitingForTokenOverlayViewOverlay(completionType=AccountCompletionType.UNDEFINED, onClose=None):
    from gui.impl.lobby.account_completion.demo_waiting_for_token_overlay_view import DemoWaitingForTokenOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(DemoWaitingForTokenOverlayView, completionType=completionType, onClose=onClose)


@waitShowOverlay
def showDemoCompleteOverlay(completionType=AccountCompletionType.UNDEFINED, onClose=None):
    from gui.impl.lobby.account_completion.demo_complete_overlay_view import DemoCompleteOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(DemoCompleteOverlayView, completionType=completionType, onClose=onClose)


@waitShowOverlay
def showDemoErrorOverlay(onClose=None):
    from gui.impl.lobby.account_completion.demo_error_overlay_view import DemoErrorOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(DemoErrorOverlayView, onClose=onClose)


@waitShowOverlay
def showDemoAccRenamingOverlay(onClose=None):
    from gui.impl.lobby.account_completion.demo_renaming_overlay_view import DemoRenamingOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(DemoRenamingOverlayView, onClose=onClose)


@waitShowOverlay
def showDemoAccRenamingCompleteOverlay(name, onClose=None):
    from gui.impl.lobby.account_completion.demo_renaming_complete_overlay_view import DemoRenamingCompleteOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(DemoRenamingCompleteOverlayView, name=name, onClose=onClose)


@waitShowOverlay
def showContactSupportOverlay(message, isCloseVisible=True, onClose=None):
    from gui.impl.lobby.account_completion.contact_support_overlay_view import ContactSupportOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(ContactSupportOverlayView, message=message, isCloseVisible=isCloseVisible, onClose=onClose)


def showModeSelectorWindow(isEventEnabled, provider=None):
    from gui.impl.lobby.mode_selector.mode_selector_view import ModeSelectorView
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    containerManager = app.containerManager
    containerManager.load(GuiImplViewLoadParams(ModeSelectorView.layoutID, ModeSelectorView, ScopeTemplates.DEFAULT_SCOPE), isEventEnabled=isEventEnabled, provider=provider)


@async
def showBuyModuleDialog(newModule, installedModule, currency, mountDisabledReason, callback):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.research.buy_module_dialog_view import BuyModuleDialogView
    result = yield await(dialogs.showSingleDialogWithResultData(module=newModule, previousModule=installedModule, currency=currency, mountDisabledReason=mountDisabledReason, layoutID=R.views.lobby.research.BuyModuleDialogView(), wrappedViewClass=BuyModuleDialogView))
    if result.busy:
        callback((False, {}))
    else:
        callback(result.result)


def showMapsTrainingPage(ctx):
    from gui.impl.lobby.maps_training.maps_training_view import MapsTrainingView
    guiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.maps_training.MapsTrainingPage()
    mapsTrainingView = guiLoader.windowsManager.getViewByLayoutID(contentResId)
    if mapsTrainingView is not None:
        mapsTrainingView.showByCtx(ctx)
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, MapsTrainingView, ScopeTemplates.DEFAULT_SCOPE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showMapsTrainingQueue():
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.maps_training.MapsTrainingQueue(), MapsTrainingQueueView, ScopeTemplates.DEFAULT_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showMapsTrainingResultsWindow(arenaUniqueID, isFromNotifications):
    from gui.impl.lobby.maps_training.maps_training_result_view import MapsTrainingResultWindow
    if not isFromNotifications:
        guiLoader = dependency.instance(IGuiLoader)
        window = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.maps_training.MapsTrainingResult())
        if window is not None:
            return
    window = MapsTrainingResultWindow(arenaUniqueID, isFromNotifications)
    window.load()
    return


@async
def showAccelerateCrewTrainingDialog(successCallback):
    from gui.impl.dialogs import dialogs
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.impl.dialogs.gf_builders import InfoDialogBuilder
    builder = InfoDialogBuilder()
    stringRoot = R.strings.dialogs.xpToTmenCheckbox
    builder.setTitle(stringRoot.title())
    builder.setDescription(stringRoot.message())
    builder.setConfirmButtonLabel(stringRoot.submit())
    builder.setCancelButtonLabel(stringRoot.cancel())
    result = yield await(dialogs.show(builder.build()))
    if result.result == DialogButtons.SUBMIT:
        successCallback()


@async
def showIdleCrewBonusDialog(description, successCallback):
    from gui.impl.dialogs import dialogs
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.impl.dialogs.gf_builders import InfoDialogBuilder
    builder = InfoDialogBuilder()
    stringRoot = R.strings.dialogs.idleCrewBonus
    builder.setTitle(stringRoot.title())
    builder.setDescription(description)
    builder.setConfirmButtonLabel(stringRoot.submit())
    builder.setCancelButtonLabel(stringRoot.cancel())
    result = yield await(dialogs.show(builder.build()))
    if result.result == DialogButtons.SUBMIT:
        successCallback()


@async
def showWotPlusRentDialog(title, description, icon, successCallback):
    from gui.impl.dialogs import dialogs
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.impl.dialogs.gf_builders import InfoDialogBuilder
    viewId = R.views.dialogs.DefaultDialog()
    uiLoader = dependency.instance(IGuiLoader)
    dtView = uiLoader.windowsManager.getViewByLayoutID(viewId)
    if dtView is not None:
        return
    else:
        builder = InfoDialogBuilder()
        stringRoot = R.strings.dialogs.wotPlusRental
        builder.setIcon(icon)
        builder.setTitle(title)
        builder.setDescription(description)
        builder.setConfirmButtonLabel(stringRoot.submit())
        builder.setCancelButtonLabel(stringRoot.cancel())
        result = yield await(dialogs.show(builder.build()))
        if result.result == DialogButtons.SUBMIT:
            successCallback()
        return


@async
def showPostProgressionPairModDialog(vehicle, stepID, modID, parent=None):
    from gui.impl.lobby.veh_post_progression.dialogs.buy_pair_modification import BuyPairModificationDialog
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=BuyPairModificationDialog, vehicle=vehicle, stepID=stepID, modID=modID, parent=parent))
    raise AsyncReturn(result)


@async
def showDestroyPairModificationsDialog(vehicle, stepIDs, parent=None):
    from gui.impl.lobby.veh_post_progression.dialogs.destroy_pair_modification import DestroyPairModificationsDialog
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=DestroyPairModificationsDialog.LAYOUT_ID, wrappedViewClass=DestroyPairModificationsDialog, vehicle=vehicle, stepIDs=stepIDs, parent=parent))
    raise AsyncReturn(result)


@async
def showPostProgressionResearchDialog(vehicle, stepIDs, parent=None):
    from gui.impl.lobby.veh_post_progression.dialogs.research_confirm import PostProgressionResearchConfirm
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.veh_post_progression.PostProgressionResearchSteps(), parent=parent, wrappedViewClass=PostProgressionResearchConfirm, vehicle=vehicle, stepIDs=stepIDs))
    raise AsyncReturn(result)


def showTelecomRentalPage():
    url = getTelecomRentVehicleUrl()
    showBrowserOverlayView(url, VIEW_ALIAS.TELECOM_RENTAL_VIEW)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showEliteWindow(vehicleCD, notificationMgr=None):
    from gui.impl.lobby.elite_window.elite_view import EliteWindow
    window = EliteWindow(vehicleCD)
    notificationMgr.append(WindowNotificationCommand(window))


def showWotPlusInfoPage():
    url = GUI_SETTINGS.renewableSubscriptionInfoPage
    showBrowserOverlayView(url, VIEW_ALIAS.WOT_PLUS_INFO_VIEW)


def showVehicleRentalPage():
    url = getRentVehicleUrl()
    showBrowserOverlayView(url, VIEW_ALIAS.VEHICLE_RENTAL_VIEW)


def showMarathonRewardScreen(marathonPrefix):
    from gui.impl.lobby.marathon.marathon_reward_window_view import MarathonRewardWindowView
    from gui.server_events.bonuses import CustomizationsBonus
    marathonController = dependency.instance(IMarathonEventsController)
    marathon = marathonController.getMarathon(marathonPrefix)
    if not marathon:
        LOG_WARNING('Could not find marathon with prefix ', marathonPrefix)
        return
    currentStage, maxStage = marathon.getMarathonProgress()
    crewRewards = []
    if marathon.isPostRewardObtained():
        remainingRewards = marathon.getStyleQuestReward()
        remainingRewards = [ reward for reward in remainingRewards if not isinstance(reward, CustomizationsBonus) ]
    elif currentStage == maxStage:
        remainingRewards = marathon.getRewardsForQuestNumber(currentStage - 1)
        crewRewards = marathon.getVehicleCrewReward()
    else:
        remainingRewards = marathon.remainingRewards
        crewRewards = marathon.getVehicleCrewReward()
    window = LobbyNotificationWindow(content=MarathonRewardWindowView({'rewards': remainingRewards,
     'crewRewards': crewRewards,
     'marathonPrefix': marathonPrefix}), layer=WindowLayer.FULLSCREEN_WINDOW)
    window.load()


def showRankedSelectableReward(rewards=None):
    from gui.impl.lobby.ranked.ranked_selectable_reward_view import RankedSelectableRewardWindow
    window = RankedSelectableRewardWindow(rewards)
    window.load()
