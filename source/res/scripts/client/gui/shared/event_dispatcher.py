# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
import logging
from operator import attrgetter
import typing
from BWUtil import AsyncReturn
import Steam
import adisp
from CurrentVehicle import HeroTankPreviewAppearance
from advanced_achievements_client.constants import TROPHIES_ACHIEVEMENT_ID
from constants import GameSeasonType, RentType
from debug_utils import LOG_WARNING
from frameworks.wulf import ViewFlags, Window, WindowFlags, WindowLayer, WindowStatus
from gui import DialogsInterface, GUI_SETTINGS, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nConfirmDialogMeta, I18nInfoDialogMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getClanQuestURL
from gui.Scaleform.daapi.view.lobby.lobby_constants import getSettingsWindowAlias
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL
from gui.Scaleform.daapi.view.lobby.shared.states import BrowserLobbyTopState
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyBattlePassUrl, getBuyCollectibleVehiclesUrl, getClientControlledCloseCtx, getShopURL, getTelecomRentVehicleUrl
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
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.clans.clan_cache import g_clanCache
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.lobby.account_completion.utils.decorators import waitShowOverlay
from gui.impl.lobby.common.congrats.common_congrats_view import CongratsWindow
from gui.impl.lobby.personal_missions_30.personal_mission_constants import IntroKeys
from gui.impl.lobby.tank_setup.dialogs.confirm_dialog import TankSetupConfirmDialog, TankSetupExitConfirmDialog
from gui.impl.lobby.tank_setup.dialogs.refill_shells import ExitFromShellsConfirm, RefillShells
from gui.impl.pub.lobby_window import LobbyNotificationWindow, LobbyWindow
from gui.impl.pub.notification_commands import EventNotificationCommand, NotificationEvent, WindowNotificationCommand
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import CTRL_ENTITY_TYPE, PREBATTLE_ACTION_NAME
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import NO_SLOT, NO_TANKMAN
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID, getNationLessName, getUserName
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.money import Currency, MONEY_UNDEFINED, Money
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
from skeletons.gui.game_control import IBattlePassController, IBoostersController, IBrowserController, IClanNotificationController, ICollectionsSystemController, IHeroTankController, IMarathonEventsController, IReferralProgramController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Generator, Iterable, List, Union, Optional
    from gui.marathon.marathon_event import MarathonEvent
    from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource
    from gui.impl.lobby.crew.widget.crew_widget import BuildedMessage
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
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


def showMissionHubIntroWindow(header, icon, description, buttonText=None):
    from gui.impl.lobby.user_missions.hub.mission_hub_intro_view import MissionHubIntroWindow
    window = MissionHubIntroWindow(header, icon, description, buttonText)
    window.load()


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


def showSkillSelectWindow():
    from gui.impl.lobby.vehicle_compare.skill_select_view import SkillSelectWindow
    uiLoader = dependency.instance(IGuiLoader)
    view = uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.vehicle_compare.SkillSelectView())
    if view is not None:
        return
    else:
        SkillSelectWindow().load()
        return


@wg_async
def showFillAllPerksDialog():
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.crew.dialogs.fill_all_perks_dialog import FillAllPerksDialog
    result = yield wg_await(dialogs.showCustomBlurSingleDialog(layoutID=FillAllPerksDialog.LAYOUT_ID, wrappedViewClass=FillAllPerksDialog))
    raise AsyncReturn(result)


def showFrontlineInfoWindow(autoscrollSection=''):
    from frontline.gui.impl.lobby.views.sub_views.info_view import InfoViewWindow
    InfoViewWindow(autoscrollSection=autoscrollSection).load()


def showBattleRoyaleLevelUpWindow(reusableInfo, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.LEVEL_UP, parent=parent), ctx={'reusableInfo': reusableInfo}), EVENT_BUS_SCOPE.LOBBY)


def showBattleRoyalePrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.BATTLE_ROYALE_PRIME_TIME), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showHangarVehicleConfigurator():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.HANGAR_VEH_INFO_VIEW), ctx={}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleInfo(vehTypeCompDescr):
    showVehicleHubOverview(int(vehTypeCompDescr))


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
    return itemPrice <= itemsCache.items.stats.money.exchange(Currency.GOLD, Currency.CREDITS, itemsCache.items.shop.exchangeRate, default=0, useDiscounts=True)


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


def showBlueprintView(vehicleCD):
    from gui.Scaleform.daapi.view.lobby.techtree.states import BlueprintState
    BlueprintState.goTo(vehicleCD=vehicleCD)


def showChangeVehicleNationDialog(vehicleCD):
    from gui.impl.lobby.nation_change.nation_change_screen import NationChangeScreen
    window = LobbyWindow(WindowFlags.WINDOW, content=NationChangeScreen(R.views.lobby.nation_change.nation_change_screen.NationChangeScreen(), ctx={'vehicleCD': vehicleCD}))
    window.load()


def showPiggyBankView():
    from gui.impl.lobby.currency_reserves.states import CurrencyReservesState
    CurrencyReservesState.goTo()


def showMapsBlacklistView():
    from gui.impl.lobby.maps_blacklist.states import MapsBlacklistState
    MapsBlacklistState.goTo()


def showDailyExpPageView(exitEvent=None):
    from gui.impl.lobby.daily_experience.states import DailyExperienceState
    DailyExperienceState.goTo()


def showDashboardView():
    from gui.impl.lobby.account_dashboard.states import AccountDashboardState
    AccountDashboardState.goTo()


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


def showResearchView(vehTypeCompDescr):
    from gui.Scaleform.daapi.view.lobby.techtree.states import ResearchState
    ResearchState.goTo(rootCD=vehTypeCompDescr)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def showTechTree(vehTypeCompDescr=None, itemsCache=None):
    from gui.Scaleform.daapi.view.lobby.techtree.states import TechtreeState
    nation = None
    if vehTypeCompDescr is not None:
        vehicle = itemsCache.items.getItemByCD(vehTypeCompDescr)
        nation = vehicle.nationName if vehicle else None
    TechtreeState.goTo(nation=nation)
    return


def showVehicleStats(vehTypeCompDescr, eventOwner=None, **kwargs):
    ctx = {'itemCD': vehTypeCompDescr,
     'eventOwner': eventOwner}
    ctx.update(**kwargs)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PROFILE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


def showHangar():
    from gui.impl.lobby.hangar.states import HangarState
    HangarState.goTo()


def showLobbyMenu():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)


def animateHangar(isShow):
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    if app is not None and app.containerManager is not None:
        hangar = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_HANGAR))
        if hangar is None:
            hangar = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LEGACY_LOBBY_HANGAR))
            if hangar:
                hangar.animateHangarSubItems(isShow)
    return


def showBarracks(location=None, nationID=None, tankType=None, role=None):
    ctx = {'location': location,
     'nationID': nationID,
     'tankType': tankType,
     'role': role}
    from gui.impl.lobby.crew.states import BarracksState
    BarracksState.goTo(**ctx)


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
    from gui.impl.lobby.dog_tags.states import DogTagState
    DogTagState.goTo(highlightedComponentId=compID, makeTopView=makeTopView)


def showAnimatedDogTags(initBackgroundId=0, initEngravingId=0):
    lobbyContext = dependency.instance(ILobbyContext)
    if not lobbyContext.getServerSettings().isDogTagCustomizationScreenEnabled():
        return
    else:
        uiLoader = dependency.instance(IGuiLoader)
        contentResId = R.views.lobby.dog_tags.AnimatedDogTagsView()
        dtView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
        if dtView is None:
            from gui.impl.lobby.dog_tags.states import AnimatedDogTagState
            AnimatedDogTagState.goTo(initBackgroundId=initBackgroundId, initEngravingId=initEngravingId)
        return


@wg_async
def showDogTagCustomizationConfirmDialog(backgroundId=None, engravingId=None, parent=None):
    from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
    from gui.impl.lobby.dog_tags.customization_confirm_dialog import CustomizationConfirmDialog
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.lobby.dog_tags.CustomizationConfirmDialog(), wrappedViewClass=CustomizationConfirmDialog, backgroundId=backgroundId, engravingId=engravingId, parent=parent))
    raise AsyncReturn(result)


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
    from gui.Scaleform.daapi.view.lobby.manual.states import ManualChapterState
    ManualChapterState.goTo(chapterIndex)


@adisp.adisp_process
def showShop(url='', path='', params=None, isClientCloseControl=False):
    from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
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
    ctx = {'url': url}
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    if app is not None and app.containerManager is not None:
        viewKey = ViewKey(VIEW_ALIAS.LOBBY_STORE)
        browserWindow = app.containerManager.getViewByKey(viewKey)
        if browserWindow is not None:
            ShopState.goTo(ctx=ctx)
            browser = browserWindow.getBrowser()
            browser.navigate(url)
            return
    if isClientCloseControl:
        ctx.update(getClientControlledCloseCtx())
    ShopState.goTo(ctx=ctx)
    return


def showStorage(defaultSection=STORAGE_CONSTANTS.FOR_SELL, tabId=None):
    from gui.Scaleform.daapi.view.lobby.storage.states import StorageState
    StorageState.goTo(defaultSection=defaultSection, defaultTab=tabId)


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
    from gui.Scaleform.daapi.view.lobby.missions.regular.states import MissionsState
    MissionsState.goTo(ctx=kwargs)


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
                else:
                    showHeroTankPreview(vehTypeCompDescr, previewAlias=previewAlias, previewBackCb=previewBackCb, previousBackAlias=previousBackAlias, hangarVehicleCD=hangarVehicleCD)
            ClientSelectableCameraObject.switchCamera(entity, 'HeroTank', instantly)
            break

    return


def showHeroTankPreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previousBackAlias=None, previewBackCb=None, hangarVehicleCD=None, backOutfit=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.HERO_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True,
     'previousBackAlias': previousBackAlias,
     'previewBackCb': previewBackCb,
     'hangarVehicleCD': hangarVehicleCD,
     'backOutfit': backOutfit}), scope=EVENT_BUS_SCOPE.LOBBY)


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


def showProfileWindow(databaseID, userName, selectedAlias=VIEW_ALIAS.PROFILE_TOTAL_PAGE, eventOwner=None):
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


def showCrewPostProgressionView():
    from gui.impl.lobby.crew.crew_post_progression_view import CrewPostProgressionWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.crew.CrewPostProgressionView()
    crewPostProgressionView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if crewPostProgressionView is None:
        window = CrewPostProgressionWindow()
        window.load()
    return


def showPersonalCase(tankmanInvID, tabId=R.views.lobby.crew.personal_case.PersonalFileView(), previousViewID=None):
    from gui.impl.lobby.crew.states import PersonalCaseState
    PersonalCaseState.goTo(currentViewID=tabId, tankmanInvID=tankmanInvID, previousViewID=previousViewID)


def showChangeCrewMember(slotIdx, vehicleInvID, parentLayoutID=None):
    from gui.impl.lobby.crew.states import MemberChangeState
    MemberChangeState.goTo(slotIdx=int(slotIdx), vehicleInvID=int(vehicleInvID), previousViewID=parentLayoutID)


def showMentorAssignment(**kwargs):
    from gui.impl.lobby.crew.mentor_assigment_view import MentorAssigmentWindow
    MentorAssigmentWindow(**kwargs).load()


def showSkillsTraining(tankmanInvID, role, callback):
    from gui.impl.lobby.crew.container_vews.skills_training.skills_training_view import SkillsTrainingWindow
    uiLoader = dependency.instance(IGuiLoader)
    if uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.crew.SkillsTrainingView()) is None:
        window = SkillsTrainingWindow(tankmanID=tankmanInvID, role=role, callback=callback)
        window.load()
    return


def showTankChange(tankmanInvID=NO_TANKMAN, slotIDX=NO_SLOT, previousViewID=None):
    from gui.impl.lobby.crew.states import TankChangeState
    TankChangeState.goTo(tankmanInvID=tankmanInvID, slotIDX=slotIDX, previousViewID=previousViewID)


def showQuickTraining(tankmanInvID=NO_TANKMAN, vehicleInvID=NO_VEHICLE_ID, previousViewID=None):
    from CurrentVehicle import g_currentVehicle
    if g_currentVehicle and vehicleInvID == NO_VEHICLE_ID:
        vehicleInvID = g_currentVehicle.invID
    from gui.impl.lobby.crew.states import QuickTrainingState
    QuickTrainingState.goTo(tankmanInvID=tankmanInvID, vehicleInvID=vehicleInvID, previousViewID=previousViewID)


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
    alias = getSettingsWindowAlias()
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias), ctx={'redefinedKeyMode': redefinedKeyMode,
     'tabIndex': tabIndex,
     'isBattleSettings': isBattleSettings}), scope=EVENT_BUS_SCOPE.GLOBAL)


def showVehicleCompare():
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.states import VehicleCompareState
    VehicleCompareState.goTo()


@pointcutable
def showCrystalWindow():
    from gui.impl.lobby.crystals_promo.states import CrystalsPromoState
    CrystalsPromoState.goTo()


@pointcutable
def openPaymentLink():
    g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.PAYMENT))


@pointcutable
def showExchangeCurrencyWindow():
    showExchangeGoldWindow()


@pointcutable
def showExchangeCurrencyWindowModal(**ctx):
    showExchangeGoldWindow(ctx=ctx, layer=WindowLayer.TOP_WINDOW, doBlur=False)


@pointcutable
def showExchangeXPWindow(needXP=None):
    ctx = None if needXP is None else {'currencyValue': needXP}
    showExchangeFreeXPWindow(ctx)
    return


@wg_async
def showExchangeXPDialogWindow(needXP=None, parent=None):
    from gui.impl.lobby.exchange.exchange_free_xp_window import ExchangeXPWindowDialog
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.dialogs import dialogs
    from gui.impl.pub.dialog_window import DialogButtons
    ctx = None if needXP is None else {'currency': needXP}
    layoutID = R.views.lobby.personal_exchange_rates.ExperienceExchangeView()
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
        wrapper = FullScreenDialogWindowWrapper(ExchangeXPWindowDialog(layoutID=layoutID, ctx=ctx), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW, doBlur=True)
        result = yield wg_await(dialogs.show(wrapper))
        status = True if result.result in DialogButtons.ACCEPT_BUTTONS else False
        raise AsyncReturn(tuple([status] + list(result.data)))
    return


@wg_async
def showVehiclesSidebarDialogWindow(parentScreen, parentWindow=None):
    from gui.impl.lobby.customization.vehicles_sidebar.vehicles_sidebar_window import VehiclesSidebarView
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.dialogs import dialogs
    layoutID = R.views.lobby.customization.vehicles_sidebar.VehiclesSidebar()
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
        wrapper = FullScreenDialogWindowWrapper(VehiclesSidebarView(layoutID=layoutID, parentScreen=parentScreen), parent=parentWindow, layer=WindowLayer.FULLSCREEN_WINDOW, doBlur=False)
        yield wg_await(dialogs.show(wrapper))
    return


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
def showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, params=None, callbackOnLoad=None, webHandlers=None, forcedSkipEscape=False, browserParams=None, hiddenLayers=None, parent=None, callbackOnClose=None):
    if not url:
        return
    else:
        if browserParams is None:
            browserParams = {}
        url = yield URLMacros().parse(url, params=params)
        ctx = {'url': url,
         'allowRightClick': False,
         'callbackOnLoad': callbackOnLoad,
         'webHandlers': webHandlers,
         'forcedSkipEscape': forcedSkipEscape,
         'browserParams': browserParams,
         'hiddenLayers': hiddenLayers or (),
         'callbackOnClose': callbackOnClose}
        if alias == VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB:
            BrowserLobbyTopState.goTo(ctx)
        else:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, parent=parent), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
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


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def showBattlePass(childStateID=R.invalid(), chapterID=0, battlePass=None, **kwargs):
    from gui.impl.lobby.battle_pass.common import getActualBattlePassIDs
    from gui.impl.lobby.battle_pass.states import BattlePassState, STATES
    if battlePass.isPaused():
        g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.ON_PAUSE))
        return
    childStateID, chapterID = getActualBattlePassIDs(childStateID, chapterID)
    guiLoader = dependency.instance(IGuiLoader)
    if guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.MainView()):
        bp = R.aliases.battle_pass
        if childStateID in (bp.Progression(), bp.PostProgression()):
            STATES[bp.ChapterChoice()].goTo()
        STATES[childStateID].goTo(chapterID=chapterID, **kwargs)
    else:
        BattlePassState.goTo(childStateID=childStateID, chapterID=chapterID, **kwargs)


def showBattlePassAwardsWindow(bonuses, data, useQueue=False, needNotifyClosing=True, packageRewards=None):
    from gui.impl.lobby.battle_pass.battle_pass_awards_view import BattlePassAwardWindow
    findAndLoadWindow(useQueue, BattlePassAwardWindow, bonuses, data, packageRewards, needNotifyClosing)


def showBattlePassHowToEarnPointsView(chapterID=0):
    from gui.impl.lobby.battle_pass.battle_pass_how_to_earn_points_view import BattlePassHowToEarnPointsWindow
    window = BattlePassHowToEarnPointsWindow(chapterID)
    window.load()


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
    from gui.Scaleform.daapi.view.lobby.customization.states import ProgressiveItemsState
    ProgressiveItemsState.goTo(itemIntCD=itemIntCD)


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
def showFrontlineConfirmDialog(skillsInteractor, vehicleType='', isBuy=True):
    from frontline.gui.impl.lobby.dialogs.reserves_confirm_dialog import ReservesConfirmDialog
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(wrappedViewClass=ReservesConfirmDialog, layoutID=ReservesConfirmDialog.LAYOUT_ID, skillsInteractor=skillsInteractor, vehicleType=vehicleType, isBuy=isBuy))
    raise AsyncReturn(result)


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
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.MainView())
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
def showOnboardingView(styleCD=None, isFirstRun=False, parent=None, guiLoader=None):
    from gui.impl.lobby.customization.progression_styles.onboarding_view import OnboardingWindow
    view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.customization.progression_styles.OnboardingView())
    if view is None:
        window = OnboardingWindow({'styleCD': styleCD,
         'isFirstRun': isFirstRun}, parent or getParentWindow())
        window.load()
    return


@wg_async
def showVehPostProgressionView(vehTypeCompDescr, overrideVehiclePreviewEvent=None, goToVehicleAllowed=False):
    from gui.impl.lobby.veh_post_progression.post_progression_intro import getPostProgressionIntroWindowProc
    intoProc = getPostProgressionIntroWindowProc()
    yield intoProc.show()
    from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
    VehiclePostProgressionState.goTo(intCD=vehTypeCompDescr, overrideVehiclePreviewEvent=overrideVehiclePreviewEvent, goToVehicleAllowed=goToVehicleAllowed)


def showVehPostProgressionCmpView(vehTypeCompDescr):
    from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionCmpState
    VehiclePostProgressionCmpState.goTo(intCD=vehTypeCompDescr)


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
    from gui.impl.lobby.mode_selector.states import ModeSelectorState
    ModeSelectorState.goTo(provider=provider, subSelectorCallback=subSelectorCallback)


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
    from gui.impl.lobby.maps_training.states import MapsTrainingState
    MapsTrainingState.goTo(ctx=ctx)


def showMapsTrainingQueue():
    from gui.impl.lobby.maps_training.states import MapsTrainingQueueState
    MapsTrainingQueueState.goTo()


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
def showResetAllPerksDialog():
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.crew.dialogs.reset_all_perks_confirm_dialog import ResetAllPerksConfirmDialog
    result = yield wg_await(dialogs.showCustomBlurSingleDialog(layoutID=ResetAllPerksConfirmDialog.LAYOUT_ID, wrappedViewClass=ResetAllPerksConfirmDialog))
    raise AsyncReturn(result)


@wg_async
def showTokenRecruitDialog(ctx):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog import TokenRecruitDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(ctx=ctx, layoutID=TokenRecruitDialog.LAYOUT_ID, wrappedViewClass=TokenRecruitDialog))
    raise AsyncReturn(result)


@wg_async
def showTankwomanRecruitAwardDialog(ctx):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.crew.dialogs.recruit_window.recruit_dialog import QuestRecruitDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(ctx=ctx, layoutID=QuestRecruitDialog.LAYOUT_ID, wrappedViewClass=QuestRecruitDialog))
    raise AsyncReturn(result)


@wg_async
def showRecruitConfirmIrrelevantConversionDialog(ctx):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.crew.dialogs.recruit_window.confirm_irrelevant_perk_reset_dialog import ConfirmIrrelevantPerkResetDialog
    result = yield wg_await(dialogs.showSingleDialogWithResultData(ctx=ctx, layoutID=ConfirmIrrelevantPerkResetDialog.LAYOUT_ID, wrappedViewClass=ConfirmIrrelevantPerkResetDialog))
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
    from gui.Scaleform.daapi.view.lobby.wot_plus.states import WotPlusInfoState
    WotPlusInfoPageLogger().logInfoPage(source, includeSubscriptionInfo)
    url = GUI_SETTINGS.renewableSubscriptionInfoPage
    url = yield URLMacros().parse(url)
    ctx = {'url': url,
     'allowRightClick': False,
     'callbackOnLoad': None,
     'webHandlers': None,
     'forcedSkipEscape': False,
     'browserParams': {},
     'hiddenLayers': (),
     'useCustomSoundSpace': useCustomSoundSpace}
    WotPlusInfoState.goTo(ctx=ctx)
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


@adisp.adisp_process
@dependency.replace_none_kwargs(boosterCtrl=IBoostersController)
def showBoostersActivation(boosterCtrl=None):
    from gui.impl.lobby.personal_reserves.states import PersonalReservesState
    if not boosterCtrl.isGameModeSupported():
        dispatcher = boosterCtrl.prbDispatcher
        if dispatcher is not None:
            result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result:
                _logger.error('Could not switch to random battle.')
        else:
            _logger.error('Prebattle dispatcher is not defined.')
    PersonalReservesState.goTo()
    return


def closeViewsWithFlags(ignoreViews, viewFlags):
    uiLoader = dependency.instance(IGuiLoader)
    for view in uiLoader.windowsManager.findViews(lambda viewToFilter: viewToFilter.viewFlags & ViewFlags.VIEW_TYPE_MASK in viewFlags):
        if view.layoutID not in ignoreViews:
            view.destroyWindow()


@dependency.replace_none_kwargs(guiLoader=IGuiLoader, collections=ICollectionsSystemController)
def showCollectionWindow(collectionId, page=None, backCallback=None, backBtnText='', parent=None, guiLoader=None, collections=None):
    if not collections.isEnabled():
        showHangar()
        return
    layoutID = R.views.lobby.collection.CollectionView()
    view = guiLoader.windowsManager.getViewByLayoutID(layoutID)
    if view:
        return
    from gui.impl.lobby.collection.collection import CollectionView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, CollectionView, ScopeTemplates.LOBBY_SUB_SCOPE), collectionId=collectionId, backCallback=backCallback, backBtnText=backBtnText, page=page), scope=EVENT_BUS_SCOPE.LOBBY)


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


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showCollectionsIntro(guiLoader=None):
    from gui.collection.account_settings import isIntroShown
    if isIntroShown():
        return
    layoutID = R.views.lobby.collection.IntroView()
    view = guiLoader.windowsManager.getViewByLayoutID(layoutID)
    if view:
        return
    from gui.impl.lobby.collection.intro_view import IntroView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, IntroView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def showWinbackIntroView(guiLoader=None):
    layoutID = R.views.lobby.winback.WinbackDailyQuestsIntroView()
    view = guiLoader.windowsManager.getViewByLayoutID(layoutID)
    if view:
        return
    from gui.impl.lobby.winback.winback_daily_quests_intro_view import WinbackDailyQuestsIntroView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, WinbackDailyQuestsIntroView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showWinbackSelectRewardView(selectableBonusTokens=None):
    from gui.impl.lobby.winback.winback_selectable_reward_view import WinbackSelectableRewardWindow
    WinbackSelectableRewardWindow(selectableBonusTokens).load()


def showAchievementEditView(*args, **kwargs):
    from gui.impl.lobby.achievements.edit_view import EditWindow
    window = EditWindow(parent=getParentWindow(), *args, **kwargs)
    window.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showSteamEmailConfirmRewardsView(rewards=None, notificationMgr=None):
    from gui.impl.lobby.account_completion.steam_email_confirm_rewards_view import SteamEmailConfirmRewardsViewWindow
    window = SteamEmailConfirmRewardsViewWindow(rewards)
    notificationMgr.append(WindowNotificationCommand(window))


def showBattlePassTankmenVoiceover(screenID, ctx=None):
    from gui.impl.lobby.battle_pass.tankmen_voiceover_view import TankmenVoiceoverWindow
    window = TankmenVoiceoverWindow(screenID=screenID, ctx=ctx)
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


def showAdvancedAchievementsCatalogView(initAchievementIDs, achievementCategory, closeCallback, parentScreen, *args, **kwargs):
    from gui.impl.lobby.achievements.catalog_view import CatalogViewWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.achievements.CatalogView()
    fullScreenWindows = uiLoader.windowsManager.findWindows(lambda w: w.layer == WindowLayer.FULLSCREEN_WINDOW)
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None and not fullScreenWindows:
        window = CatalogViewWindow(initAchievementIDs=initAchievementIDs, achievementCategory=achievementCategory, closeCallback=closeCallback, uiParentScreen=parentScreen, *args, **kwargs)
        window.load()
    return


def showTrophiesView(closeCallback, parentScreen, *args, **kwargs):
    from gui.impl.lobby.achievements.catalog_view import CatalogViewWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.achievements.CatalogView()
    fullScreenWindows = uiLoader.windowsManager.findWindows(lambda w: w.layer == WindowLayer.FULLSCREEN_WINDOW)
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None and not fullScreenWindows:
        window = CatalogViewWindow(initAchievementIDs=[TROPHIES_ACHIEVEMENT_ID], achievementCategory='', closeCallback=closeCallback, uiParentScreen=parentScreen, *args, **kwargs)
        window.load()
    return


def showAdvancedAchievementsView(closeCallback=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PROFILE), ctx={'selectedAlias': VIEW_ALIAS.PROFILE_ACHIEVEMENTS_PAGE,
     'closeCallback': closeCallback}), scope=EVENT_BUS_SCOPE.LOBBY)


def showAdvancedAchievementsRewardView(bonusTuples, *args, **kwargs):
    from gui.impl.lobby.achievements.reward_view import RewardViewWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.achievements.RewardView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        window = RewardViewWindow(bonusTuples=bonusTuples, *args, **kwargs)
        window.load()
    return


@wg_async
def showExchangeGoldWindow(ctx=None, layer=WindowLayer.FULLSCREEN_WINDOW, doBlur=True):
    from gui.impl.lobby.exchange.exchange_gold_window import ExchangeGoldView
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.dialogs import dialogs
    layoutID = R.views.lobby.personal_exchange_rates.GoldExchangeView()
    guiLoader = dependency.instance(IGuiLoader)
    ctx = ctx or {}
    ctx.setdefault('blur', doBlur)
    if guiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
        yield dialogs.showSimple(FullScreenDialogWindowWrapper(ExchangeGoldView(layoutID=layoutID, ctx=ctx), doBlur=False, layer=layer))
    return


@wg_async
def showExchangeFreeXPWindow(ctx=None, doBlur=True):
    from gui.impl.lobby.exchange.exchange_free_xp_window import ExchangeFreeXPView
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
    from gui.impl.dialogs import dialogs
    layoutID = R.views.lobby.personal_exchange_rates.ExperienceExchangeView()
    guiLoader = dependency.instance(IGuiLoader)
    ctx = ctx or {}
    ctx.setdefault('blur', doBlur)
    if guiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
        yield dialogs.showSimple(FullScreenDialogWindowWrapper(ExchangeFreeXPView(layoutID=layoutID, ctx=ctx), doBlur=False, layer=WindowLayer.FULLSCREEN_WINDOW))
    return


def showEasyTankEquipScreen(*args, **kwargs):
    from gui.impl.lobby.easy_tank_equip.states import EasyTankEquipState
    EasyTankEquipState.goTo()


@wg_async
def showExchangeToApplyEasyTankEquipDialog(price, availableGoldAmount, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.easy_tank_equip.dialogs.easy_tank_equip_exchange_dialog import ExchangeToApplyEasyTankEquip
    result = yield wg_await(dialogs.showSingleDialog(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToApplyEasyTankEquip(), parent=parent, wrappedViewClass=ExchangeToApplyEasyTankEquip, price=price, availableGoldAmount=availableGoldAmount))
    raise AsyncReturn(result)


@wg_async
def showAlternateConfigurationDialog(vehIntCD, feature, nodeID, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.veh_skill_tree.dialogs.alternate_configuration_dialog import AlternateConfigurationDialog
    result = yield wg_await(dialogs.showSingleDialog(layoutID=R.views.mono.lobby.veh_skill_tree.dialogs.alternate_configuration(), parent=parent, wrappedViewClass=AlternateConfigurationDialog, vehIntCD=vehIntCD, feature=feature, nodeID=nodeID))
    raise AsyncReturn(result)


@wg_async
def showResearchConfirmDialog(researchedItemsText, xp, freeXP, parent=None):
    from gui.impl.dialogs import dialogs
    from gui.impl.lobby.dialogs.research_confirm import ResearchConfirmDialogWindow
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.mono.dialogs.research_confirm_dialog(), parent=parent, wrappedViewClass=ResearchConfirmDialogWindow, researchedItemsText=researchedItemsText, xp=xp, freeXP=freeXP))
    raise AsyncReturn(result)


def showRandomBattleResultsWindow(arenaUniqueID, bonusType):
    from gui.impl.lobby.battle_results.states import PostBattleResultsEntryState
    PostBattleResultsEntryState.goTo(arenaUniqueID=arenaUniqueID, bonusType=bonusType)


def showCustomizationRarityAwardScreen(element, isFirstEntry):
    from gui.impl.lobby.customization.customization_rarity_reward_screen.customization_rarity_reward_screen import CustomizationRarityRewardWindow
    window = CustomizationRarityRewardWindow(element, isFirstEntry)
    window.load()


def showVanityRarityAwardScreen(element):
    from gui.impl.lobby.veh_skill_tree.rarity_reward_screen.rarity_reward_screen import RarityRewardWindow
    window = RarityRewardWindow(element)
    window.load()


def showViewByAlias(alias, parent=None, **kwargs):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, parent=parent), **kwargs), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehicleHubOverview(intCD, vehicleStrCD=None, style=None, outfit=None):
    from gui.impl.lobby.vehicle_hub import VehicleHubCtx, OverviewState
    OverviewState.goTo(vhCtx=VehicleHubCtx(intCD=intCD, vehicleStrCD=vehicleStrCD, style=style, outfit=outfit))


def showVehicleHubModules(intCD, vehicleStrCD=None, style=None, outfit=None):
    from gui.impl.lobby.vehicle_hub import VehicleHubCtx, ModulesState
    ModulesState.goTo(vhCtx=VehicleHubCtx(intCD=intCD, vehicleStrCD=vehicleStrCD, style=style, outfit=outfit))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def showVehicleHubVehSkillTree(intCD, vehicleStrCD=None, style=None, outfit=None, itemsCache=None):
    from gui.impl.lobby.vehicle_hub import VehicleHubCtx, VehSkillTreeState
    vehicle = itemsCache.items.getItemByCD(intCD)
    if vehicle is not None and vehicle.postProgression.isVehSkillTree():
        VehSkillTreeState.goTo(vhCtx=VehicleHubCtx(intCD=intCD, vehicleStrCD=vehicleStrCD, style=style, outfit=outfit))
    return


def showVehicleHubVehSkillTreePrestige(intCD, vehicleStrCD=None, style=None, outfit=None):
    from gui.impl.lobby.vehicle_hub import VehicleHubCtx, VehSkillTreePrestigeState
    VehSkillTreePrestigeState.goTo(vhCtx=VehicleHubCtx(intCD=intCD, vehicleStrCD=vehicleStrCD, style=style, outfit=outfit))


def showVehSkillTreeIntro():
    from gui.impl.lobby.veh_skill_tree.dialogs.intro_page_view import IntroPageWindow
    window = IntroPageWindow()
    window.load()


def showVehicleHubStats(intCD, vehicleStrCD=None, style=None, outfit=None):
    from gui.impl.lobby.vehicle_hub import VehicleHubCtx, StatsState
    StatsState.goTo(vhCtx=VehicleHubCtx(intCD=intCD, vehicleStrCD=vehicleStrCD, style=style, outfit=outfit))


def showVehicleHubArmor(intCD, vehicleStrCD=None, style=None, outfit=None):
    from gui.impl.lobby.vehicle_hub import VehicleHubCtx, ArmorState
    ArmorState.goTo(vhCtx=VehicleHubCtx(intCD=intCD, vehicleStrCD=vehicleStrCD, style=style, outfit=outfit))


def showVehicleHubMechanicsVideo(mechanicsName):
    urlDict = GUI_SETTINGS.lookup('mechanicsVideoUrls')
    if urlDict is None:
        logging.warning('There is no mechanicsVideoUrls in gui_settings config.')
        return
    else:
        url = urlDict.get(mechanicsName)
        showBrowserOverlayView(url, VIEW_ALIAS.BROWSER_OVERLAY)
        return


def showPersonalMissionCampaignSelectorWindow():
    from gui.impl.lobby.personal_missions_30.state import CampaignSelectorState
    CampaignSelectorState.goTo()


def showPersonalMissionMainWindow(operationID, state=None):
    from gui.Scaleform.lobby_entry import getLobbyStateMachine
    from gui.impl.lobby.personal_missions_30.state import PersonalMissions3EntryState
    if not getLobbyStateMachine().isStateEntered(PersonalMissions3EntryState.STATE_ID):
        PersonalMissions3EntryState.goTo(operationID=operationID, state=state)


def showPersonalMissionChain(operationID, missionCategory, state=None):
    from gui.impl.lobby.personal_missions_30.state import MissionsState
    MissionsState.goTo(operationID=operationID, category=missionCategory, state=state)


def showPM30IntroWindow(force=False):
    from gui.impl.lobby.personal_missions_30.intro_view import MainIntroViewWindow
    from gui.impl.lobby.personal_missions_30.views_helpers import isIntroShown, markIntroShown
    introKey = IntroKeys.MAIN_INTRO_VIEW.value
    if not isIntroShown(introKey) or force:
        if not force:
            markIntroShown(introKey)
        pmCampaignIntroView = MainIntroViewWindow()
        pmCampaignIntroView.load()


def showPM30OperationIntroWindow(operationID, force=False):
    from gui.impl.lobby.personal_missions_30.intro_view import OperationIntroViewWindow
    from gui.impl.lobby.personal_missions_30.views_helpers import isIntroShown, markIntroShown
    introKey = IntroKeys.OPERATION_INTRO_VIEW.value % operationID
    if not isIntroShown(introKey) or force:
        if not force:
            markIntroShown(introKey)
        pmCampaignIntroView = OperationIntroViewWindow(operationID)
        pmCampaignIntroView.load()


def showPM30OperationAssemblingVideoWindow(operationID, stageNumber, closingCallback=None):
    from gui.impl.lobby.personal_missions_30.stage_view import AssemblingVideoViewWindow
    pmAssemblingVideoView = AssemblingVideoViewWindow(operationID, stageNumber, closingCallback=closingCallback)
    pmAssemblingVideoView.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showPM30RewardsWindow(ctx, notificationMgr=None):
    from gui.impl.lobby.personal_missions_30.rewards_view import RewardsViewWindow
    window = RewardsViewWindow(ctx)
    notificationMgr.append(WindowNotificationCommand(window))
