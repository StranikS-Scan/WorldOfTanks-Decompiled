# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
import logging
from operator import attrgetter
import Steam
import adisp
import typing
from BWUtil import AsyncReturn
from shared_utils import first
from CurrentVehicle import HeroTankPreviewAppearance
from constants import GameSeasonType, RentType
from debug_utils import LOG_WARNING
from frameworks.wulf import ViewFlags, Window, WindowFlags, WindowLayer, WindowStatus
from gui import DialogsInterface, GUI_SETTINGS, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nConfirmDialogMeta, I18nInfoDialogMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getClanQuestURL
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyCollectibleVehiclesUrl, getClientControlledCloseCtx, getShopURL, getTelecomRentVehicleUrl, getBuyBattlePassUrl
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, SFViewLoadParams
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.MAPBOX_ALIASES import MAPBOX_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.clans.clan_cache import g_clanCache
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.lobby.account_completion.utils.decorators import waitShowOverlay
from gui.impl.lobby.battle_royale import BATTLE_ROYALE_LOCK_SOURCE_NAME
from gui.impl.lobby.common.congrats.common_congrats_view import CongratsWindow
from gui.impl.lobby.tank_setup.dialogs.confirm_dialog import TankSetupConfirmDialog, TankSetupExitConfirmDialog
from gui.impl.lobby.tank_setup.dialogs.refill_shells import ExitFromShellsConfirm, RefillShells
from gui.impl.pub.lobby_window import LobbyNotificationWindow, LobbyWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand, NonPersistentEventNotificationCommand, NotificationEvent, EventNotificationCommand
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.resource_well.resource import Resource
from gui.resource_well.resource_well_helpers import isResourceWellRewardVehicle
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import NO_TANKMAN
from gui.shared.gui_items.Vehicle import getNationLessName, getUserName, NO_VEHICLE_ID
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.lock_overlays import lockNotificationManager
from gui.shared.money import Currency, MONEY_UNDEFINED, Money
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getUniqueViewName, getViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shop import showBlueprintsExchangeOverlay, showBuyGoldForRentWebOverlay, showBuyProductOverlay
from helpers import dependency
from helpers.aop import pointcutable
from items import ITEM_TYPES, parseIntCompactDescr, vehicles as vehicles_core
from nations import NAMES
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBrowserController, IClanNotificationController, ICollectionsSystemController, IHeroTankController, IMarathonEventsController, IReferralProgramController, IResourceWellController, IBoostersController, IComp7Controller
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Generator, Iterable, List, Union, Tuple, Optional
    from gui.marathon.marathon_event import MarathonEvent
    from enum import Enum
    from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource
    from gui.impl.lobby.crew.widget.crew_widget import BuildedMessage
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


def showComp7PrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showRankedBattleIntro():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS)), scope=EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_PRIME_TIME_ALIAS), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesAfterBattleWindow(levelUpInfo, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS, parent=parent), ctx={'levelUpInfo': levelUpInfo}), EVENT_BUS_SCOPE.LOBBY)


def showFrontlineContainerWindow(activeTab=None):
    from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_container_tab_model import TabType
    from frontline.gui.impl.lobby.views.frontline_container_view import FrontlineContainerView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.frontline.lobby.FrontlineContainerView(), FrontlineContainerView, ScopeTemplates.VIEW_SCOPE), activeTab=activeTab if activeTab else TabType.PROGRESS), scope=EVENT_BUS_SCOPE.LOBBY)


def closeFrontlineContainerWindow():
    g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(layoutID=R.views.frontline.lobby.FrontlineContainerView()))


def showFrontlineWelcomeWindow():
    from frontline.gui.impl.lobby.views.welcome_view import WelcomeViewWindow
    WelcomeViewWindow().load()


def showFrontlineInfoWindow(autoscrollSection=''):
    from frontline.gui.impl.lobby.views.sub_views.info_view import InfoViewWindow
    InfoViewWindow(autoscrollSection=autoscrollSection).load()


def showBattleRoyaleLevelUpWindow(reusableInfo, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.LEVEL_UP, parent=parent), ctx={'reusableInfo': reusableInfo}), EVENT_BUS_SCOPE.LOBBY)


def showBattleRoyalePrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME), ctx={}), EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showBattleRoyaleResultsView(ctx, notificationsMgr=None):
    notificationsMgr.append(NonPersistentEventNotificationCommand(NotificationEvent(method=showBattleRoyaleResultsInfo, ctx=ctx)))


def showBattleRoyaleResultsInfo(ctx):
    lockNotificationManager(True, source=BATTLE_ROYALE_LOCK_SOURCE_NAME)
    from gui.impl.lobby.battle_royale.battle_result_view import BrBattleResultsViewInLobby
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.battle_royale.BattleResultView()
    battleResultView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if battleResultView is not None:
        if battleResultView.arenaUniqueID == ctx.get('arenaUniqueID', -1):
            return
        g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(layoutID=contentResId))
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, BrBattleResultsViewInLobby, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showHangarVehicleConfigurator():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW), ctx={}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleInfo(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEHICLE_INFO_WINDOW, getViewName(VIEW_ALIAS.VEHICLE_INFO_WINDOW, int(vehTypeCompDescr))), ctx={'vehicleCompactDescr': int(vehTypeCompDescr)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleRentDialog(intCD, rentType, nums, seasonType, price, buyParams):
    if not (seasonType == GameSeasonType.EPIC and rentType in (RentType.SEASON_RENT, RentType.SEASON_CYCLE_RENT)):
        _logger.debug('GameSeasonType %s with RentType %s is not supported', seasonType, rentType)
        return
    priceCode = buyParams['priceCode']
    if price.get(priceCode) != buyParams['priceAmount']:
        price = Money(**{priceCode: buyParams['priceAmount']})
    _purchaseOffer(intCD, rentType, nums, price, seasonType, buyParams, renew=False)


@adisp.adisp_process
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


@adisp.adisp_process
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


def showGoodieInfo(goodieID):
    goodieID = int(goodieID)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.GOODIE_INFO_WINDOW, getViewName(VIEW_ALIAS.GOODIE_INFO_WINDOW, goodieID)), ctx={'goodieID': goodieID}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleSellDialog(vehInvID):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.VEHICLE_SELL_DIALOG), ctx={'vehInvID': int(vehInvID)}), EVENT_BUS_SCOPE.LOBBY)


def showVehicleBuyDialog(vehicle, actionType=None, isTradeIn=False, previousAlias=None, returnAlias=None, returnCallback=None, ctx=None):
    from gui.impl.lobby.hangar.buy_vehicle_view import BuyVehicleWindow
    ctx = ctx or {}
    ctx.update({'nationID': vehicle.nationID,
     'itemID': vehicle.innationID,
     'actionType': actionType,
     'isTradeIn': isTradeIn,
     'previousAlias': previousAlias,
     'returnAlias': returnAlias,
     'returnCallback': returnCallback})
    window = BuyVehicleWindow(ctx=ctx)
    window.load()


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
    from gui.impl.lobby.currency_reserves.currency_reserves_view import CurrencyReservesView
    viewId = R.views.lobby.currency_reserves.CurrencyReserves()
    params = GuiImplViewLoadParams(viewId, CurrencyReservesView, ScopeTemplates.LOBBY_SUB_SCOPE)
    uiLoader = dependency.instance(IGuiLoader)
    dtView = uiLoader.windowsManager.getViewByLayoutID(viewId)
    if dtView is not None:
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(params), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showMapsBlacklistView():
    from gui.impl.lobby.premacc.maps_blacklist_view import MapsBlacklistView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=R.views.lobby.excluded_maps.ExcludedMapsView(), viewClass=MapsBlacklistView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showCrew5075Welcome():
    from gui.impl.lobby.crew.crew_intro_view import CrewIntroWindow
    CrewIntroWindow().load()


def showDailyExpPageView(exitEvent=None):
    from gui.impl.lobby.account_dashboard.daily_experience_view import DailyExperienceView
    viewId = R.views.lobby.account_dashboard.DailyExperienceView()
    params = GuiImplViewLoadParams(viewId, DailyExperienceView, ScopeTemplates.LOBBY_SUB_SCOPE)
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(params), scope=EVENT_BUS_SCOPE.LOBBY)


def showDashboardView():
    from gui.impl.lobby.account_dashboard.account_dashboard_view import AccountDashboardView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.account_dashboard.AccountDashboard(), AccountDashboardView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


@wg_async
def showBattleBoosterBuyDialog(battleBoosterIntCD):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.lobby.instructions.booster_buy_dialog import BoosterBuyWindowView
    wrapper = FullScreenDialogWindowWrapper(BoosterBuyWindowView(battleBoosterIntCD))
    yield dialogs.showSimple(wrapper)


@wg_async
def showBattleBoosterSellDialog(battleBoosterIntCD):
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.lobby.instructions.booster_sell_dialog import BoosterSellWindowView
    from gui.impl.dialogs import dialogs
    wrapper = FullScreenDialogWindowWrapper(BoosterSellWindowView(battleBoosterIntCD))
    yield dialogs.showSimple(wrapper)


@wg_async
def showPlatoonWarningDialog(resources):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import WarningDialogBuilder
    from gui.impl.pub.dialog_window import DialogButtons
    builder = WarningDialogBuilder()
    builder.setTitle(resources.title())
    builder.setMessagesAndButtons(message=resources, buttons=resources, focused=DialogButtons.CANCEL)
    result = yield wg_await(dialogs.showSimple(builder.buildInLobby()))
    raise AsyncReturn(result)


@wg_async
def showPlatoonInfoDialog(resources):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import ResSimpleDialogBuilder
    from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
    from gui.impl.pub.dialog_window import DialogButtons
    builder = ResSimpleDialogBuilder()
    builder.setTitle(resources.title())
    builder.setPreset(DialogPresets.CUSTOMIZATION_INSTALL_BOUND)
    builder.setMessagesAndButtons(message=resources, buttons=resources, focused=DialogButtons.SUBMIT)
    result = yield wg_await(dialogs.showSimple(builder.buildInLobby()))
    raise AsyncReturn(result)


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


def showVehicleStats(vehTypeCompDescr, eventOwner=None, **kwargs):
    ctx = {'itemCD': vehTypeCompDescr,
     'eventOwner': eventOwner}
    ctx.update(**kwargs)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PROFILE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showHangar():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)


def showBarracks(location=None, nationID=None, tankType=None, role=None):
    from gui.impl.lobby.crew.barracks_view import BarracksView
    uiLoader = dependency.instance(IGuiLoader)
    layoutID = R.views.lobby.crew.BarracksView()
    if uiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=layoutID, viewClass=BarracksView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'location': location,
         'nationID': nationID,
         'tankType': tankType,
         'role': role}), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showJunkTankmenConversion():
    from gui.impl.lobby.crew.conversion_confirm_view import ConversionConfirmWindow
    ConversionConfirmWindow().load()


def showConversionAwardsView(**kwargs):
    from gui.impl.lobby.crew.conversion_awards_view import ConversionAwardsWindow
    ConversionAwardsWindow(**kwargs).load()


def showJunkTankmen():
    from gui.impl.lobby.crew.junk_tankmen_view import JunkTankmenWindow
    JunkTankmenWindow().load()


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


def showStrongholds(url=None, reloadView=False):
    strongholdProvider = g_clanCache.strongholdProvider
    browserCtrl = dependency.instance(IBrowserController)
    browserIsActive = browserCtrl is not None and browserCtrl.getAllBrowsers()
    if browserIsActive and strongholdProvider is not None and strongholdProvider.isTabActive() and not reloadView:
        strongholdProvider.loadUrl(url)
    else:
        ctx = {'url': url} if url is not None else {}
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STRONGHOLD), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def openManualPage(chapterIndex):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MANUAL_CHAPTER_VIEW), ctx={'chapterIndex': chapterIndex}), EVENT_BUS_SCOPE.LOBBY)


@adisp.adisp_process
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


def showConfigurableVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previewBackCb=None, hiddenBlocks=None, itemPack=None, **kwargs):
    kwargs.update({'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewBackCb': previewBackCb,
     'hiddenBlocks': hiddenBlocks,
     'itemsPack': itemPack})
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW), ctx=kwargs), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None, itemsPack=None, offers=None, price=MONEY_UNDEFINED, oldPrice=None, title='', description=None, endTime=None, buyParams=None, obtainingMethod=None, vehParams=None, **kwargs):
    heroTankController = dependency.instance(IHeroTankController)
    heroTankCD = heroTankController.getCurrentTankCD()
    isHeroTank = heroTankCD and heroTankCD == vehTypeCompDescr
    if isHeroTank and not (itemsPack or offers or vehParams):
        goToHeroTankOnScene(vehTypeCompDescr, previewAlias, previewBackCb=previewBackCb, instantly=True)
    else:
        from ClientSelectableCameraObject import ClientSelectableCameraObject
        ClientSelectableCameraObject.switchCamera()
        vehicle = dependency.instance(IItemsCache).items.getItemByCD(vehTypeCompDescr)
        if not (itemsPack or offers or vehParams) and vehicle.canTradeIn:
            viewAlias = VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW
        elif offers and offers[0].eventType == 'telecom_rentals':
            viewAlias = VIEW_ALIAS.RENTAL_VEHICLE_PREVIEW
        else:
            viewAlias = VIEW_ALIAS.VEHICLE_PREVIEW
        app = dependency.instance(IAppLoader).getApp()
        view = app.containerManager.getViewByKey(ViewKey(viewAlias))
        if view is not None:
            view.destroy()
        kwargs.update({'itemCD': vehTypeCompDescr,
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
         'obtainingMethod': obtainingMethod,
         'vehParams': vehParams})
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(viewAlias), ctx=kwargs), EVENT_BUS_SCOPE.LOBBY)
    return


def showVehiclePreviewWithoutBottomPanel(vehCD, backCallback=None, previewAlias=None, **kwargs):
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import OptionalBlocks
    kwargs.update({'itemCD': vehCD,
     'previewBackCb': backCallback,
     'hiddenBlocks': (OptionalBlocks.CLOSE_BUTTON, OptionalBlocks.BUYING_PANEL),
     'previewAlias': previewAlias or VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW})
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW), ctx=kwargs), EVENT_BUS_SCOPE.LOBBY)


def showConfigurableShopVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previewBackCb=None, hiddenBlocks=None, itemPack=None, **kwargs):
    heroTankController = dependency.instance(IHeroTankController)
    heroTankCD = heroTankController.getCurrentTankCD()
    if heroTankCD and heroTankCD == vehTypeCompDescr and not itemPack:
        goToHeroTankOnScene(vehTypeCompDescr, previewAlias, previewBackCb=previewBackCb, instantly=True)
    else:
        from ClientSelectableCameraObject import ClientSelectableCameraObject
        ClientSelectableCameraObject.switchCamera()
        showConfigurableVehiclePreview(vehTypeCompDescr, previewAlias, previewBackCb, hiddenBlocks, itemPack, **kwargs)


def showDelayedReward():
    kwargs = {'tab': QUESTS_ALIASES.BATTLE_MATTERS_VIEW_PY_ALIAS,
     'openVehicleSelection': True}
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MISSIONS), ctx=kwargs), scope=EVENT_BUS_SCOPE.LOBBY)


def goToHeroTankOnScene(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previewBackCb=None, previousBackAlias=None, hangarVehicleCD=None, instantly=False):
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
                elif isResourceWellRewardVehicle(descriptor.type.compactDescr):
                    showResourceWellHeroPreview(descriptor.type.compactDescr, previewAlias=previewAlias, previousBackAlias=previousBackAlias)
                else:
                    showHeroTankPreview(vehTypeCompDescr, previewAlias=previewAlias, previewBackCb=previewBackCb, previousBackAlias=previousBackAlias, hangarVehicleCD=hangarVehicleCD)
            ClientSelectableCameraObject.switchCamera(entity, 'HeroTank', instantly)
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


def showMissionAwardWindow(award):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MISSION_AWARD_WINDOW, name=getUniqueViewName(VIEW_ALIAS.MISSION_AWARD_WINDOW)), ctx={'award': award}), EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showPersonalMissionsQuestAwardScreen(quest, ctx, proxyEvent, notificationMgr=None):
    alias = PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_QUEST_AWARD_SCREEN_ALIAS
    window = SFWindow(SFViewLoadParams(alias, getUniqueViewName(alias)), ctx={'quest': quest,
     'ctxData': ctx,
     'proxyEvent': proxyEvent}, scope=EVENT_BUS_SCOPE.LOBBY)
    notificationMgr.append(WindowNotificationCommand(window))


def showProfileWindow(databaseID, userName, selectedAlias=None, eventOwner=None):
    alias = VIEW_ALIAS.PROFILE_WINDOW
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, getViewName(alias, databaseID)), ctx={'userName': userName,
     'databaseID': databaseID,
     'selectedAlias': selectedAlias,
     'eventOwner': eventOwner}), EVENT_BUS_SCOPE.LOBBY)


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
    g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, ctx={'vehicleInvID': veh.invID,
     'prevVehicleInvID': g_currentVehicle.invID}), scope=EVENT_BUS_SCOPE.LOBBY)
    g_currentVehicle.selectVehicle(veh.invID)
    if loadHangar:
        showHangar()


def showCrewAboutView(navigateFrom=None):
    from gui.impl.lobby.crew.help_view import HelpViewWindow
    HelpViewWindow(navigateFrom=navigateFrom).load()


def showPersonalCase(tankmanInvID, tabId=R.views.lobby.crew.personal_case.PersonalFileView(), previousViewID=None):
    from gui.impl.lobby.crew.tankman_container_view import TankmanContainerView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.crew.TankmanContainerView()
    personalCaseView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if personalCaseView is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=TankmanContainerView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), currentViewID=tabId, tankmanInvID=tankmanInvID, previousViewID=previousViewID), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        personalCaseView.updateTankmanId(tankmanInvID)
        personalCaseView.updateTabId(tabId)
        personalCaseView.bringToFront()
    return


def showChangeCrewMember(slotIdx, vehicleInvID, parentLayoutID=None):
    from gui.impl.lobby.crew.member_change_view import MemberChangeView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.crew.MemberChangeView()
    changeCrewMemberView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if changeCrewMemberView is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=MemberChangeView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), slotIdx=int(slotIdx), vehicleInvID=int(vehicleInvID), previousViewID=parentLayoutID), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        changeCrewMemberView.selectSlot(slotIdx)
        changeCrewMemberView.bringToFront()
    return


def showTankChange(tankmanInvID=NO_TANKMAN, previousViewID=None):
    from gui.impl.lobby.crew.tank_change_view import TankChangeView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.crew.TankChangeView()
    tankChangeView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if tankChangeView is None or tankmanInvID not in (NO_TANKMAN, tankChangeView.selectedTmanInvID):
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=TankChangeView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), tankmanInvID=tankmanInvID, previousViewID=previousViewID), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        tankChangeView.bringToFront()
    return


def showQuickTraining(tankmanInvID=NO_TANKMAN, vehicleInvID=NO_VEHICLE_ID, previousViewID=None):
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.crew.QuickTrainingView()
    quickTrainingView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if quickTrainingView is None:
        from gui.impl.lobby.crew.quick_training_view import QuickTrainingView
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=QuickTrainingView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), tankmanInvID=tankmanInvID, vehicleInvID=vehicleInvID, previousViewID=previousViewID), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        quickTrainingView.bringToFront()
    return


def showCollectibleVehicles(nationID):
    nationName = NAMES[nationID]
    showShop(getBuyCollectibleVehiclesUrl(), nationName)


@adisp.adisp_async
@adisp.adisp_process
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


def runSalesChain(chapterID, restoreIfRun=True, reloadIfRun=False, isStopForced=False):
    g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.START_TRAINING, settingsID='SALES_TRIGGERS', initialChapter=chapterID, restoreIfRun=restoreIfRun, reloadIfRun=reloadIfRun, isStopForced=isStopForced))


def changeAppResolution(width, height, scale):
    g_eventBus.handleEvent(events.GameEvent(events.GameEvent.CHANGE_APP_RESOLUTION, ctx={'width': width,
     'height': height,
     'scale': scale}), scope=EVENT_BUS_SCOPE.GLOBAL)


@adisp.adisp_process
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
def showCrystalWindow():
    from gui.impl.lobby.crystals_promo.crystals_promo_view import CrystalsPromoView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.crystalsPromo.CrystalsPromoView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, CrystalsPromoView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@pointcutable
def openPaymentLink():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PAYMENT))


@pointcutable
def showExchangeCurrencyWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EXCHANGE_WINDOW)), EVENT_BUS_SCOPE.LOBBY)


@pointcutable
def showExchangeCurrencyWindowModal(**ctx):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EXCHANGE_WINDOW_MODAL), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)


@pointcutable
def showExchangeXPWindow(needXP=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EXCHANGE_XP_WINDOW), ctx={'needXP': needXP}), EVENT_BUS_SCOPE.LOBBY)


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


@adisp.adisp_process
def showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, params=None, callbackOnLoad=None, webHandlers=None, forcedSkipEscape=False, browserParams=None, hiddenLayers=None, parent=None):
    if url:
        if browserParams is None:
            browserParams = {}
        url = yield URLMacros().parse(url, params=params)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, parent=parent), ctx={'url': url,
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
def showSeniorityRewardVehiclesWindow(vehicles=None, fromEntryPoint=True, notificationMgr=None):
    from gui.impl.lobby.seniority_awards.seniority_awards_vehicles_view import SeniorityRewardVehiclesWindow
    viewID = R.views.lobby.seniority_awards.SeniorityVehiclesAwardsView()
    uiLoader = dependency.instance(IGuiLoader)
    if uiLoader.windowsManager.getViewByLayoutID(viewID) is None:
        window = SeniorityRewardVehiclesWindow(viewID, vehicles, fromEntryPoint)
        notificationMgr.append(WindowNotificationCommand(window))
    else:
        _logger.error('SeniorityRewardVehiclesWindow already exists')
    return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showSeniorityRewardAwardWindow(data, notificationMgr=None):
    from gui.impl.lobby.seniority_awards.seniority_reward_award_view import SeniorityRewardAwardWindow
    viewID = R.views.lobby.seniority_awards.SeniorityAwardsView()
    uiLoader = dependency.instance(IGuiLoader)
    if uiLoader.windowsManager.getViewByLayoutID(viewID) is None:
        window = SeniorityRewardAwardWindow(data, viewID)
        notificationMgr.append(WindowNotificationCommand(window))
    else:
        _logger.error('SeniorityRewardAwardWindow already exists')
    return


def showBattlePassAwardsWindow(bonuses, data, useQueue=False, needNotifyClosing=True, packageRewards=None):
    from gui.impl.lobby.battle_pass.battle_pass_awards_view import BattlePassAwardWindow
    findAndLoadWindow(useQueue, BattlePassAwardWindow, bonuses, data, packageRewards, needNotifyClosing)


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


def showStylePreview(vehCD, style, descr='', backCallback=None, backBtnDescrLabel='', *args, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STYLE_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': descr,
     'backCallback': backCallback,
     'backPreviewAlias': kwargs.get('backPreviewAlias'),
     'backBtnDescrLabel': backBtnDescrLabel,
     'topPanelData': kwargs.get('topPanelData'),
     'itemsPack': kwargs.get('itemsPack'),
     'outfit': kwargs.get('outfit')}), scope=EVENT_BUS_SCOPE.LOBBY)


def showStyleProgressionPreview(vehCD, style, descr, backCallback, backBtnDescrLabel='', *args, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': descr,
     'backCallback': backCallback,
     'backPreviewAlias': kwargs.get('backPreviewAlias'),
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
     'backPreviewAlias': kwargs.get('backPreviewAlias'),
     'backBtnDescrLabel': backBtnDescrLabel,
     'styleLevel': kwargs.get('styleLevel'),
     'price': kwargs.get('price'),
     'buyParams': kwargs.get('buyParams')}), scope=EVENT_BUS_SCOPE.LOBBY)


def showShowcaseStyleBuyingPreview(vehCD, style, descr, backCallback, backBtnDescrLabel='', *args, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.SHOWCASE_STYLE_BUYING_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': descr,
     'backCallback': backCallback,
     'backPreviewAlias': kwargs.get('backPreviewAlias'),
     'backBtnDescrLabel': backBtnDescrLabel,
     'price': kwargs.get('price'),
     'originalPrice': kwargs.get('originalPrice'),
     'buyParams': kwargs.get('buyParams'),
     'obtainingMethod': kwargs.get('obtainingMethod'),
     'endTime': kwargs.get('endTime'),
     'discountPercent': kwargs.get('discountPercent')}), scope=EVENT_BUS_SCOPE.LOBBY)


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


@wg_async
def showPreformattedDialog(preset, title, message, buttons, focusedButton, btnDownSounds):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import FormattedSimpleDialogBuilder
    builder = FormattedSimpleDialogBuilder()
    builder.setMessagesAndButtons(preset, title, message, buttons, focusedButton, btnDownSounds)
    result = yield wg_await(dialogs.show(builder.build()))
    raise AsyncReturn(result)


@wg_async
def showResSimpleDialog(resources, icon, formattedMessage, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import ResSimpleDialogBuilder
    builder = ResSimpleDialogBuilder()
    builder.setMessagesAndButtons(resources)
    builder.setIcon(icon)
    builder.setFormattedMessage(formattedMessage)
    result = yield wg_await(dialogs.showSimple(builder.buildInLobby(parent)))
    raise AsyncReturn(result)


@wg_async
def showDynamicButtonInfoDialogBuilder(resources, icon, formattedMessage, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import InfoDialogBuilder
    builder = InfoDialogBuilder()
    builder.setMessagesAndButtons(resources, resources)
    builder.setIcon(icon)
    builder.setFormattedMessage(formattedMessage)
    result = yield wg_await(dialogs.showSimple(builder.build(parent)))
    raise AsyncReturn(result)


@wg_async
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
    result, dontShowAgain = yield wg_await(dialogs.showSimpleWithResultData(builder.build(parent=parent)))
    if result and dontShowAgain:
        serverSettings.saveInUIStorage({UI_STORAGE_KEYS.DISABLE_EDITABLE_STYLE_REWRITE_WARNING: True})
    raise AsyncReturn(result)
    return


@wg_async
def showDialog(dialog, callback):
    from gui.impl.dialogs import dialogs
    isOk = yield wg_await(dialogs.showSimple(dialog))
    callback((isOk, {}))


@wg_async
def showOptDeviceCommonWindowDialog(wrappedViewClass, deviceDescr=None, layoutID=None):
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(compDescr=deviceDescr, layoutID=layoutID or R.views.lobby.demountkit.CommonWindow(), wrappedViewClass=wrappedViewClass))
    if result.busy:
        raise AsyncReturn((False, {}))
    else:
        isOk, _ = result.result
        raise AsyncReturn((isOk, {}))


@wg_async
def showOptionalDeviceDestroy(itemCD, callback):
    from gui.impl.dialogs.gf_builders import WarningDialogBuilder
    builder = WarningDialogBuilder()
    builder.setConfirmButtonLabel(R.strings.dialogs.removeConfirmationNotRemovable.submit())
    optionalDevice = dependency.instance(IItemsCache).items.getItemByCD(itemCD)
    title = backport.text(R.strings.dialogs.equipmentDestroy.conformation(), equipment=optionalDevice.userName)
    builder.setTitle(title)
    builder.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
    from gui.impl.dialogs.dialog_template import DialogTemplateView
    result = yield wg_await(showOptDeviceCommonWindowDialog(lambda **_: builder.buildView(), layoutID=DialogTemplateView.LAYOUT_ID))
    callback(result)


@wg_async
def showOptionalDeviceDemount(deviceDescr, callback, forFitting=False):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.demount_kit.demount_dialog import DemountOptionalDeviceDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(itemCD=deviceDescr, forFitting=forFitting, layoutID=DemountOptionalDeviceDialog.LAYOUT_ID, wrappedViewClass=DemountOptionalDeviceDialog))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        if data.get('openSingleDemountWindow', False):
            showOptionalDeviceDemountSinglePrice(deviceDescr, callback, forFitting=forFitting)
        else:
            callback((isOK, data))


@wg_async
def showOptionalDeviceDemountSinglePrice(deviceDescr, callback, forFitting=False):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.demount_kit.demount_single_price_dialog import DemountOptionalDeviceSinglePriceDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(itemCD=deviceDescr, forFitting=forFitting, layoutID=DemountOptionalDeviceSinglePriceDialog.LAYOUT_ID, wrappedViewClass=DemountOptionalDeviceSinglePriceDialog))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        if data.get('openDemountSelectorWindow', False):
            showOptionalDeviceDemount(deviceDescr, callback, forFitting=forFitting)
        else:
            callback((isOK, data))


@wg_async
def showOptionalDeviceDemountFromSlot(deviceDescr, callback, forFitting=False, vehicle=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.demount_kit.demount_from_slot_dialog import DemountOptionalDeviceFromSlotDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(itemCD=deviceDescr, forFitting=forFitting, vehicle=vehicle, layoutID=DemountOptionalDeviceFromSlotDialog.LAYOUT_ID, wrappedViewClass=DemountOptionalDeviceFromSlotDialog))
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
    from gui.impl.lobby.offers.offer_banner_window import OfferBannerWindow
    layoutID = R.views.lobby.offers.OfferGiftsWindow()
    _killOldView(layoutID)
    if OfferBannerWindow.isLoaded(offerID):
        OfferBannerWindow.destroyBannerWindow(offerID)
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, OfferGiftsWindow, ScopeTemplates.LOBBY_SUB_SCOPE), offerID=offerID, overrideSuccessCallback=overrideSuccessCallback), scope=EVENT_BUS_SCOPE.LOBBY)


@wg_async
def showOfferGiftDialog(offerID, giftID, cdnTitle='', callback=None):
    from gui.impl.lobby.offers.offer_gift_dialog import makeOfferGiftDialog
    dialogBuilder = makeOfferGiftDialog(offerID, giftID, cdnTitle)
    app = dependency.instance(IAppLoader).getApp()
    view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
    yield showDialog(dialogBuilder.build(parent=view), callback)


@wg_async
def showBonusDelayedConfirmationDialog(vehicle, callback=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.lobby.battle_matters.battle_matters_exchange_rewards import BattleMattersExchangeRewards
    vehicleUserName = vehicle.userName
    vehicleName = getNationLessName(vehicle.name)
    result = yield wg_await(dialogs.showSimple(FullScreenDialogWindowWrapper(BattleMattersExchangeRewards(vehicleName, vehicleUserName))))
    callback(result)


def showOfferGiftVehiclePreview(offerID, giftID, confirmCallback=None, backBtnLabel=None, customCallbacks=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW), ctx={'offerID': offerID,
     'giftID': giftID,
     'confirmCallback': confirmCallback,
     'backBtnLabel': backBtnLabel,
     'customCallbacks': customCallbacks}), scope=EVENT_BUS_SCOPE.LOBBY)


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
    progressiveItemsView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if progressiveItemsView is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=ProgressiveItemsView, scope=ScopeTemplates.LOBBY_SUB_SCOPE, parent=parent), view, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, itemIntCD=itemIntCD), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        progressiveItemsView.update()
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


@wg_async
def showNeedRepairDialog(vehicle, wrappedViewClass, repairClazz, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.NeedRepair(), wrappedViewClass=wrappedViewClass, vehicle=vehicle, startState=startState, parent=parent, repairClazz=repairClazz))
    raise AsyncReturn(result)


@wg_async
def showTankSetupConfirmDialog(items, vehicle=None, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=TankSetupConfirmDialog, items=items, vehicle=vehicle, startState=startState, parent=parent))
    raise AsyncReturn(result)


@wg_async
def showTankSetupExitConfirmDialog(items, vehicle=None, startState=None, fromSection=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=TankSetupExitConfirmDialog, items=items, vehicle=vehicle, startState=startState, fromSection=fromSection, parent=parent))
    raise AsyncReturn(result)


@wg_async
def showRefillShellsDialog(price, shells, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.RefillShells(), wrappedViewClass=RefillShells, price=price, shells=shells, startState=startState, parent=parent))
    raise AsyncReturn(result)


@wg_async
def showExitFromShellsDialog(price, shells, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.RefillShells(), wrappedViewClass=ExitFromShellsConfirm, price=price, shells=shells, startState=startState, parent=parent))
    raise AsyncReturn(result)


@wg_async
def showBattleAbilitiesConfirmDialog(items, vehicleType, withInstall=None, parent=None, applyForAllVehiclesByType=False):
    from gui.impl.lobby.tank_setup.dialogs.battle_abilities_confirm import BattleAbilitiesSetupConfirm
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=BattleAbilitiesSetupConfirm, items=items, withInstall=withInstall, parent=parent, vehicleType=vehicleType, applyForAllVehiclesByType=applyForAllVehiclesByType))
    raise AsyncReturn(result)


def showBlueprintsSalePage(url=None):
    showBlueprintsExchangeOverlay(url=url)


@wg_async
def showActiveTestConfirmDialog(startTime, finishTime, link, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.matchmaker.active_test_confirm_view import ActiveTestConfirmView
    result = yield wg_await(dialogs.showSingleDialog(layoutID=R.views.lobby.matchmaker.ActiveTestConfirmView(), wrappedViewClass=ActiveTestConfirmView, startTime=startTime, finishTime=finishTime, link=link, parent=parent))
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


def showEpicRewardsSelectionWindow(onRewardsReceivedCallback=None, onCloseCallback=None, onLoadedCallback=None, isAutoDestroyWindowsOnReceivedRewards=True, level=0):
    from gui.impl.lobby.frontline.rewards_selection_view import RewardsSelectionWindow
    window = RewardsSelectionWindow(onRewardsReceivedCallback, onCloseCallback, onLoadedCallback, isAutoDestroyWindowsOnReceivedRewards, level)
    window.load()
    return window


def showFrontlineAwards(bonuses, onCloseCallback=None, onAnimationEndedCallback=None, useQueue=False):
    from frontline.gui.impl.lobby.views.awards_view import AwardsWindow
    findAndLoadWindow(useQueue, AwardsWindow, bonuses, onCloseCallback=onCloseCallback, onAnimationEndedCallback=onAnimationEndedCallback)


@wg_async
def showFrontlineConfirmDialog(skillIds, vehicleType='', applyForAllOfType=False, isBuy=True):
    from frontline.gui.impl.lobby.dialogs.reserves_confirm_dialog import ReservesConfirmDialog
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(wrappedViewClass=ReservesConfirmDialog, layoutID=ReservesConfirmDialog.LAYOUT_ID, skillIds=skillIds, vehicleType=vehicleType, applyForAllOfType=applyForAllOfType, isBuy=isBuy))
    raise AsyncReturn(result)


def showBlankGiftWindow(itemCD, count):
    from gui.impl.lobby.blank_gift.awards_view import BlankGiftWindow
    BlankGiftWindow(itemCD, count).load()


def showNewLevelWindow(pLevel=1, cLevel=2, pXp=50, cXp=70, boosterFlXP=30, originalFlXP=10, rank=1):
    extensionInfo = {'metaLevel': (cLevel, cXp),
     'prevMetaLevel': (pLevel, pXp),
     'playerRank': rank,
     'boosterFlXP': boosterFlXP,
     'originalFlXP': originalFlXP}
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS), ctx={'levelUpInfo': extensionInfo}), EVENT_BUS_SCOPE.LOBBY)


@wg_async
@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showBattlePassActivateChapterConfirmDialog(chapterID, callback, guiLoader=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.battle_pass.activate_chapter_confirm_dialog import ActivateChapterConfirmDialog
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.BattlePassProgressionsView())
    result = yield wg_await(dialogs.showSingleDialogWithResultData(chapterID=chapterID, layoutID=ActivateChapterConfirmDialog.LAYOUT_ID, wrappedViewClass=ActivateChapterConfirmDialog, parent=view.getParentWindow()))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showDeconstructionDeviceWindow(ctx=None, parent=None, guiLoader=None, upgradedPair=None, onDeconstructedCallback=None):
    from gui.impl.lobby.tank_setup.deconstruction_device_view import DeconstructionDeviceWindow
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.tanksetup.DeconstructionDeviceView())
    if view is None:
        window = DeconstructionDeviceWindow(upgradedPair, parent or getParentWindow(), onDeconstructedCallback=onDeconstructedCallback)
        window.load()
    return


@wg_async
def showDeconstructionMultDeviceDialog(ctx):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.tank_setup.dialogs.deconstruct_confirm import DeconstructMultConfirm
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=DeconstructMultConfirm.LAYOUT_ID, ctx=ctx, wrappedViewClass=DeconstructMultConfirm))
    raise AsyncReturn(result.result)


@wg_async
def showDeconstructionDeviceDialog(itemIntCD, fromVehicle=False):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.tank_setup.dialogs.deconstruct_confirm import DeconstructConfirm
    result = yield wg_await(dialogs.showSingleDialogWithResultData(itemIntCD=itemIntCD, fromVehicle=fromVehicle, layoutID=DeconstructConfirm.LAYOUT_ID, wrappedViewClass=DeconstructConfirm))
    raise AsyncReturn(result.result)


@adisp.adisp_process
@dependency.replace_none_kwargs(guiLoader=IGuiLoader, itemsCache=IItemsCache)
def showSellDialog(itemIntCD, guiLoader=None, itemsCache=None, parent=None):
    from gui.shared.gui_items import GUI_ITEM_TYPE
    from gui.impl.lobby.tank_setup.dialogs.module_deconstruct_dialogs import DeconstructDialogWindow
    from gui.impl.lobby.tank_setup.dialogs.opt_device_sell_dialog import OptDeviceSellDialogWindow
    item = itemsCache.items.getItemByCD(itemIntCD)
    if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        if item.isModernized:
            view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.tanksetup.dialogs.ConfirmActionsWithEquipmentDialog())
            if view is None:
                window = DeconstructDialogWindow(itemIntCD, parent or getParentWindow())
                window.load()
                yield lambda callback: callback(True)
                return
        view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.tanksetup.dialogs.Sell())
        if view is None:
            window = OptDeviceSellDialogWindow(itemIntCD, parent or getParentWindow())
            window.load()
            yield lambda callback: callback(True)
            return
    yield DialogsInterface.showDialog(SellModuleMeta(int(itemIntCD)))
    return


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


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showOnboardingView(styleCD=None, isFirstRun=False, parent=None, guiLoader=None):
    from gui.impl.lobby.customization.progression_styles.onboarding_view import OnboardingWindow
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.customization.progression_styles.OnboardingView())
    if view is None:
        window = OnboardingWindow({'styleCD': styleCD,
         'isFirstRun': isFirstRun}, parent or getParentWindow())
        window.load()
    return


@wg_async
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


def getParentWindow():
    guiLoader = dependency.instance(IGuiLoader)
    windows = guiLoader.windowsManager.findWindows(lambda w: w.layer == WindowLayer.SUB_VIEW)
    return first(windows)


def showMapboxPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(MAPBOX_ALIASES.MAPBOX_PRIME_TIME), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showMapboxIntro(closeCallback=None):
    from gui.impl.lobby.mapbox.map_box_intro import MapBoxIntro
    layoutID = R.views.lobby.mapbox.MapBoxIntro()
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(layoutID) is not None:
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, MapBoxIntro, ScopeTemplates.LOBBY_SUB_SCOPE), closeCallback=closeCallback), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showMapboxSurvey(mapName, closeCallback=None):
    from gui.impl.lobby.mapbox.mapbox_survey_view import MapBoxSurveyWindow
    if not MapBoxSurveyWindow.getInstances():
        window = MapBoxSurveyWindow(mapName, closeCallback)
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
def showSteamConfirmEmailOverlay(email='', onClose=None):
    from gui.impl.lobby.account_completion.steam_confirm_email_overlay_view import SteamConfirmEmailOverlayView
    from gui.impl.lobby.account_completion.curtain.curtain_view import CurtainWindow
    wnd = CurtainWindow.getInstance()
    wnd.setSubView(SteamConfirmEmailOverlayView, email=email, onClose=onClose)


def showModeSelectorWindow(provider=None, subSelectorCallback=None):
    from gui.impl.lobby.mode_selector.mode_selector_view import ModeSelectorView
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.mode_selector.ModeSelectorView()) is not None:
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(ModeSelectorView.layoutID, ModeSelectorView, ScopeTemplates.VIEW_SCOPE), provider=provider, subSelectorCallback=subSelectorCallback), scope=EVENT_BUS_SCOPE.LOBBY)
        return


@wg_async
def showBuyModuleDialog(newModule, installedModule, currency, mountDisabledReason, callback):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.research.buy_module_dialog_view import BuyModuleDialogView
    result = yield wg_await(dialogs.showSingleDialogWithResultData(module=newModule, previousModule=installedModule, currency=currency, mountDisabledReason=mountDisabledReason, layoutID=R.views.lobby.research.BuyModuleDialogView(), wrappedViewClass=BuyModuleDialogView))
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
    from gui.impl.lobby.maps_training.maps_training_queue_view import MapsTrainingQueueView
    _killOldView(R.views.lobby.maps_training.MapsTrainingQueue())
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


@wg_async
def showAccelerateCrewTrainingDialog(successCallback):
    from gui.impl.dialogs import dialogs
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.impl.dialogs.gf_builders import AcceleratedCrewTrainingDialogBuilder
    builder = AcceleratedCrewTrainingDialogBuilder()
    stringRoot = R.strings.dialogs.xpToTmenCheckbox
    builder.setTitle(stringRoot.title())
    builder.setDescription(stringRoot.message())
    builder.setConfirmButtonLabel(stringRoot.submit())
    builder.setCancelButtonLabel(stringRoot.cancel())
    result = yield wg_await(dialogs.show(builder.build()))
    if result.result == DialogButtons.SUBMIT:
        successCallback()


@wg_async
def showIdleCrewBonusDialog(description, successCallback):
    from gui.impl.dialogs import dialogs
    from gui.impl.pub.dialog_window import DialogButtons
    from gui.impl.dialogs.gf_builders import PassiveXPDialogBuilder
    builder = PassiveXPDialogBuilder()
    stringRoot = R.strings.dialogs.idleCrewBonus
    builder.setTitle(stringRoot.title())
    builder.setDescriptionMsg(description.text)
    builder.setMessageIconFrom(description.iconFrom)
    builder.setMessageIconTo(description.iconTo)
    builder.setConfirmButtonLabel(stringRoot.submit())
    builder.setCancelButtonLabel(stringRoot.cancel())
    builder.setVehiclesCD([description.vehFromCD, description.vehToCD])
    result = yield wg_await(dialogs.show(builder.build()))
    if result.result == DialogButtons.SUBMIT:
        successCallback()


@wg_async
def showTelecomRentDialog(title, description, icon, successCallback):
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
        result = yield wg_await(dialogs.show(builder.build()))
        if result.result == DialogButtons.SUBMIT:
            successCallback()
        return


@wg_async
def showPostProgressionPairModDialog(vehicle, stepID, modID, parent=None):
    from gui.impl.lobby.veh_post_progression.dialogs.buy_pair_modification import BuyPairModificationDialog
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=BuyPairModificationDialog, vehicle=vehicle, stepID=stepID, modID=modID, parent=parent))
    raise AsyncReturn(result)


@wg_async
def showDestroyPairModificationsDialog(vehicle, stepIDs, parent=None):
    from gui.impl.lobby.veh_post_progression.dialogs.destroy_pair_modification import DestroyPairModificationsDialog
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=DestroyPairModificationsDialog.LAYOUT_ID, wrappedViewClass=DestroyPairModificationsDialog, vehicle=vehicle, stepIDs=stepIDs, parent=parent))
    raise AsyncReturn(result)


@wg_async
def showPostProgressionResearchDialog(vehicle, stepIDs, parent=None):
    from gui.impl.lobby.veh_post_progression.dialogs.research_confirm import PostProgressionResearchConfirm
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.veh_post_progression.PostProgressionResearchSteps(), parent=parent, wrappedViewClass=PostProgressionResearchConfirm, vehicle=vehicle, stepIDs=stepIDs))
    raise AsyncReturn(result)


@wg_async
def showTokenRecruitDialog(ctx, parentViewKey=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog import TokenRecruitDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(ctx=ctx, parentViewKey=parentViewKey, layoutID=TokenRecruitDialog.LAYOUT_ID, wrappedViewClass=TokenRecruitDialog))
    raise AsyncReturn(result)


@wg_async
def showTankwomanRecruitAwardDialog(ctx, parentViewKey=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog import QuestRecruitDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(ctx=ctx, parentViewKey=parentViewKey, layoutID=QuestRecruitDialog.LAYOUT_ID, wrappedViewClass=QuestRecruitDialog))
    raise AsyncReturn(result)


def showTelecomRentalPage():
    url = getTelecomRentVehicleUrl()
    showBrowserOverlayView(url, VIEW_ALIAS.TELECOM_RENTAL_VIEW)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showEliteWindow(vehicleCD, notificationMgr=None):
    from gui.impl.lobby.elite_window.elite_view import EliteWindow
    window = EliteWindow(vehicleCD)
    notificationMgr.append(WindowNotificationCommand(window))


@adisp.adisp_process
def showWotPlusInfoPage(source, useCustomSoundSpace=False, includeSubscriptionInfo=False):
    from uilogging.wot_plus.loggers import WotPlusInfoPageLogger
    WotPlusInfoPageLogger().logInfoPage(source, includeSubscriptionInfo)
    url = GUI_SETTINGS.renewableSubscriptionInfoPage
    alias = VIEW_ALIAS.WOT_PLUS_INFO_VIEW
    url = yield URLMacros().parse(url)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias), ctx={'url': url,
     'allowRightClick': False,
     'callbackOnLoad': None,
     'webHandlers': None,
     'forcedSkipEscape': False,
     'browserParams': {},
     'hiddenLayers': (),
     'useCustomSoundSpace': useCustomSoundSpace}), EVENT_BUS_SCOPE.LOBBY)
    return


def showSteamRedirectWotPlus():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.WOT_PLUS_STEAM_SHOP))


def showWotPlusProductPage():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.WOT_PLUS_SHOP))


def showWotPlusSteamSubscriptionManagementPage():
    if Steam.isOverlayEnabled():
        Steam.activateGameOverlayToWebPage(GUI_SETTINGS.steamSubscriptionManagementURL)
    else:
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.STEAM_SUBSCRIPTION_MANAGEMENT))


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


def showSubscriptionsPage():
    from gui.impl.lobby.player_subscriptions.player_subscriptions_view import PlayerSubscriptionsView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.player_subscriptions.PlayerSubscriptions(), PlayerSubscriptionsView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def showResourceWellProgressionWindow(resourceWell=None, backCallback=showHangar):
    from gui.impl.lobby.resource_well.completed_progression_view import CompletedProgressionView
    from gui.impl.lobby.resource_well.progression_view import ProgressionView
    if resourceWell.isCompleted():
        view = CompletedProgressionView
        viewRes = R.views.lobby.resource_well.CompletedProgressionView()
    else:
        view = ProgressionView
        viewRes = R.views.lobby.resource_well.ProgressionView()
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(viewRes) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(viewRes, view, ScopeTemplates.DEFAULT_SCOPE), backCallback=backCallback), scope=EVENT_BUS_SCOPE.LOBBY)
    return


def showResourcesLoadingWindow():
    from gui.impl.lobby.resource_well.resources_loading_view import ResourcesLoadingWindow
    ResourcesLoadingWindow().load()


@wg_async
def showResourcesLoadingConfirm(resources, isReturnOperation, callback):
    from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
    from gui.impl.lobby.resource_well.resources_loading_confirm import ResourcesLoadingConfirm
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.lobby.resource_well.ResourcesLoadingConfirm(), wrappedViewClass=ResourcesLoadingConfirm, resources=resources, isReturnOperation=isReturnOperation))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


@wg_async
def showResourceWellNoSerialVehiclesConfirm(callback):
    from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
    from gui.impl.lobby.resource_well.no_serial_vehicles_confirm import NoSerialVehiclesConfirm
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.lobby.resource_well.NoSerialVehiclesConfirm(), wrappedViewClass=NoSerialVehiclesConfirm))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        callback((isOK, data))


def showResourceWellNoVehiclesConfirm():
    from gui.impl.lobby.resource_well.no_vehicles_confirm import NoVehiclesConfirmWindow
    NoVehiclesConfirmWindow().load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showResourceWellAwardWindow(serialNumber='', notificationMgr=None):
    from gui.impl.lobby.resource_well.award_view import AwardWindow
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.resource_well.AwardView()) is None:
        window = AwardWindow(serialNumber=serialNumber)
        _killOldView(R.views.lobby.resource_well.ProgressionView())
        _killOldView(R.views.lobby.resource_well.ResourcesLoadingView())
        notificationMgr.append(WindowNotificationCommand(window))
    return


def showResourceWellVehiclePreview(vehicleCD, style=None, backCallback=None, topPanelData=None):
    if topPanelData is not None and topPanelData.get('currentTabID') == TabID.PERSONAL_NUMBER_VEHICLE:
        previewStyle = style
    else:
        previewStyle = None
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW), ctx={'itemCD': vehicleCD,
     'previewBackCb': backCallback,
     'numberStyle': style,
     'style': previewStyle,
     'topPanelData': topPanelData,
     'previewAlias': VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW}), EVENT_BUS_SCOPE.LOBBY)
    return


def showResourceWellHeroPreview(vehicleCD, backCallback=None, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previousBackAlias=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.RESOURCE_WELL_HERO_VEHICLE_PREVIEW), ctx={'itemCD': vehicleCD,
     'previewBackCb': backCallback,
     'previewAlias': previewAlias,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True,
     'previousBackAlias': previousBackAlias}), EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showBattleMattersReward(ctx=None, notificationMgr=None):
    from gui.impl.lobby.battle_matters.battle_matters_rewards_view import BattleMattersRewardsViewWindow
    if ctx is not None:
        window = BattleMattersRewardsViewWindow(ctx=ctx)
        notificationMgr.append(WindowNotificationCommand(window))
    else:
        _logger.error('No context for BattleMatters rewards View')
    return


def showPersonalReservesInfomationScreen():
    url = GUI_SETTINGS.personalReservesInfoPage
    showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)


def showPersonalReservesIntro():
    from gui.impl.lobby.personal_reserves.personal_reserves_intro import PersonalReservesIntroWindow
    from gui.server_events.settings import personalReservesSettings
    with personalReservesSettings() as prSettings:
        prSettings.setIsIntroPageShown(True)
    if not PersonalReservesIntroWindow.getInstances():
        PersonalReservesIntroWindow().load()


def showBoostersActivation():
    uiLoader = dependency.instance(IGuiLoader)
    controller = dependency.instance(IBoostersController)
    contentResId = R.views.lobby.personal_reserves.ReservesActivationView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        if not controller.isGameModeSupported():
            controller.selectRandomBattle()
        from gui.impl.lobby.personal_reserves.reserves_activation_view import ReservesActivationView
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, ReservesActivationView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
    else:
        closeViewsWithFlags([R.views.lobby.personal_reserves.ReservesActivationView()], [ViewFlags.LOBBY_TOP_SUB_VIEW])
    return


def closeViewsWithFlags(ignoreViews, viewFlags):
    uiLoader = dependency.instance(IGuiLoader)
    for view in uiLoader.windowsManager.findViews(lambda viewToFilter: viewToFilter.viewFlags & ViewFlags.VIEW_TYPE_MASK in viewFlags):
        if view.layoutID not in ignoreViews:
            view.destroyWindow()


def showComp7MetaRootView(tabId=None, *args, **kwargs):
    from gui.impl.lobby.comp7.meta_view.meta_root_view import MetaRootView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.comp7.MetaRootView()
    metaView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if metaView is None:
        g_eventBus.handleEvent(events.Comp7Event(events.Comp7Event.OPEN_META), scope=EVENT_BUS_SCOPE.LOBBY)
        event = events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, MetaRootView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId=tabId, *args, **kwargs)
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
    elif tabId is not None:
        metaView.switchPage(tabId)
    return


def showComp7NoVehiclesScreen():
    from gui.impl.lobby.comp7.no_vehicles_screen import NoVehiclesScreenWindow
    if not NoVehiclesScreenWindow.getInstances():
        NoVehiclesScreenWindow(parent=getParentWindow()).load()


def showComp7IntroScreen():
    from gui.impl.lobby.comp7.intro_screen import IntroScreen
    event = events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.comp7.IntroScreen(), IntroScreen, ScopeTemplates.LOBBY_SUB_SCOPE))
    g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7WhatsNewScreen(notificationMgr=None):
    from gui.impl.lobby.comp7.whats_new_view import WhatsNewViewWindow
    notificationMgr.append(WindowNotificationCommand(WhatsNewViewWindow()))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7RanksRewardsScreen(quest, periodicQuests, notificationMgr=None):
    from gui.impl.lobby.comp7.rewards_screen import RanksRewardsScreenWindow
    window = RanksRewardsScreenWindow(quest=quest, periodicQuests=periodicQuests)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7TokensRewardsScreen(quest, notificationMgr=None):
    from gui.impl.lobby.comp7.rewards_screen import TokensRewardsScreenWindow
    window = TokensRewardsScreenWindow(quest=quest)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showComp7QualificationRewardsScreen(quests, notificationMgr=None):
    from gui.impl.lobby.comp7.rewards_screen import QualificationRewardsScreenWindow
    window = QualificationRewardsScreenWindow(quests=quests)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController, comp7Ctrl=IComp7Controller)
def showComp7SeasonStatisticsScreen(seasonNumber=None, force=False, notificationMgr=None, comp7Ctrl=None):
    from gui.impl.lobby.comp7.season_statistics import SeasonStatisticsWindow
    if not seasonNumber:
        seasonInfo = comp7Ctrl.getPreviousSeason()
        if not seasonInfo:
            _logger.error('Could not show Season Statistic view, no season info.')
            return
        seasonNumber = comp7Ctrl.getPreviousSeason().getNumber()
    window = SeasonStatisticsWindow(seasonNumber=seasonNumber, saveViewing=not force)
    if force:
        window.load()
    else:
        notificationMgr.append(WindowNotificationCommand(window))


def showComp7PurchaseDialog(productCode):
    from gui.impl.lobby.comp7.dialogs.purchase_dialog import PurchaseDialogWindow
    if not PurchaseDialogWindow.getInstances():
        PurchaseDialogWindow(productCode).load()


@dependency.replace_none_kwargs(guiLoader=IGuiLoader, collections=ICollectionsSystemController)
def showCollectionWindow(collectionId, page=None, backCallback=None, backBtnText='', parent=None, guiLoader=None, collections=None):
    if not collections.isEnabled():
        showHangar()
        return
    else:
        from gui.impl.lobby.collection.collection import CollectionWindow
        view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.collection.CollectionView())
        if view is None:
            window = CollectionWindow(collectionId, page, backCallback, backBtnText, parent or getParentWindow())
            window.load()
        return


def showCollectionsMainPage():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PROFILE), ctx={'selectedAlias': VIEW_ALIAS.PROFILE_COLLECTIONS_PAGE}), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(guiLoader=IGuiLoader, collections=ICollectionsSystemController)
def showCollectionItemPreviewWindow(itemId, collectionId, page, pagesCount, backCallback, backBtnText, guiLoader=None, collections=None):
    if not collections.isEnabled():
        showHangar()
        return
    else:
        from gui.impl.lobby.collection.collection_item_preview import CollectionItemPreviewWindow
        view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.collection.CollectionItemPreview())
        if view is None:
            window = CollectionItemPreviewWindow(itemId, collectionId, page, pagesCount, backCallback, backBtnText)
            window.load()
        return


@dependency.replace_none_kwargs(guiLoader=IGuiLoader, notificationMgr=INotificationWindowController)
def showCollectionAwardsWindow(collectionId, bonuses, guiLoader=None, notificationMgr=None):
    from gui.impl.lobby.collection.awards_view import AwardsWindow
    if guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.collection.AwardsView()) is None:
        window = AwardsWindow(collectionId, bonuses)
        notificationMgr.append(WindowNotificationCommand(window))
    return


def showCollectionsIntro():
    from gui.collection.account_settings import isIntroShown
    if not isIntroShown():
        from gui.impl.lobby.collection.intro_view import IntroWindow
        window = IntroWindow(parent=getParentWindow())
        window.load()


def showWinbackIntroView(parent=None):
    from gui.impl.lobby.winback.winback_daily_quests_intro_view import WinbackDailyQuestsIntroWindow
    window = WinbackDailyQuestsIntroWindow(parent=parent if parent is not None else getParentWindow())
    window.load()
    return


def showWinbackSelectRewardView(selectableBonusTokens=None):
    from gui.impl.lobby.winback.winback_selectable_reward_view import WinbackSelectableRewardWindow
    WinbackSelectableRewardWindow(selectableBonusTokens).load()


def showAchievementEditView(*args, **kwargs):
    from gui.impl.lobby.achievements.edit_view import EditWindow
    window = EditWindow(parent=getParentWindow(), *args, **kwargs)
    window.load()


def showWotPlusIntroView():
    from gui.impl.lobby.subscription.wot_plus_intro_view import WotPlusIntroView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.subscription.WotPlusIntroView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, WotPlusIntroView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showSteamEmailConfirmRewardsView(rewards=None, notificationMgr=None):
    from gui.impl.lobby.account_completion.steam_email_confirm_rewards_view import SteamEmailConfirmRewardsViewWindow
    window = SteamEmailConfirmRewardsViewWindow(rewards)
    notificationMgr.append(WindowNotificationCommand(window))


def showBattlePassTankmenVoiceover(ctx=None):
    from gui.impl.lobby.battle_pass.custom_tankmen_voiceover_view import CustomTankmenVoiceoverWindow
    window = CustomTankmenVoiceoverWindow(ctx=ctx)
    window.load()


@adisp.adisp_process
def showBuyBattlePassOverlay(parent=None):
    url = getBuyBattlePassUrl()
    if url:
        url = yield URLMacros().parse(url)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BROWSER_OVERLAY, parent=parent), ctx={'url': url}), EVENT_BUS_SCOPE.LOBBY)


def showPrebattleHintsWindow(hintModel, hintsViewClass=None):
    from gui.impl.battle.prebattle.prebattle_hints_view import PrebattleHintsWindow, PrebattleHintsView
    hintsViewClass = hintsViewClass or PrebattleHintsView
    needToShow = getattr(hintsViewClass, 'needToShow')
    if not callable(needToShow) or needToShow():
        window = PrebattleHintsWindow(hintModel, hintsViewClass)
        window.load()


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showPrebattleHintsConfirmWindow(notificationsMgr=None):
    from gui.impl.battle.prebattle.prebattle_hints_confirm import showPrebattleHintsConfirm
    notificationsMgr.append(EventNotificationCommand(NotificationEvent(method=showPrebattleHintsConfirm)))
