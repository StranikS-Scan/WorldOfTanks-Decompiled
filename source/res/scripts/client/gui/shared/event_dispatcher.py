# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_dispatcher.py
import logging
from operator import attrgetter
import typing
from BWUtil import AsyncReturn
import adisp
from CurrentVehicle import HeroTankPreviewAppearance
from async import async, await
from constants import RentType, GameSeasonType, QUEUE_TYPE
from debug_utils import LOG_WARNING
from frameworks.wulf import ViewFlags
from frameworks.wulf import Window
from frameworks.wulf import WindowFlags, WindowStatus
from gui import SystemMessages, DialogsInterface, GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta, I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsWebProductMeta
from gui.Scaleform.daapi.view.dialogs.rent_confirm_dialog import RentConfirmDialogMeta
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getClanQuestURL
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL, getBuyCollectibleVehiclesUrl
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams, GuiImplViewLoadParams
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.genConsts.EPICBATTLES_ALIASES import EPICBATTLES_ALIASES
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.battle.battle_royale.battle_result_view import BrBattleResultsViewInBattle
from gui.impl.gen import R
from gui.impl.lobby.demount_kit.optional_device_dialogs import BuyAndInstallOpDevDialog, BuyAndStorageOpDevDialog, DemountOpDevSinglePriceDialog, DestroyOpDevDialog, InstallOpDevDialog
from gui.impl.lobby.demount_kit.selector_dialog import DemountOpDevDialog
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.offers.offer_gift_dialog import makeOfferGiftDialog
from gui.impl.lobby.tank_setup.dialogs.battle_abilities_confirm import BattleAbilitiesSetupConfirm
from gui.impl.lobby.tank_setup.dialogs.confirm_dialog import TankSetupConfirmDialog, TankSetupExitConfirmDialog
from gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepair
from gui.impl.lobby.tank_setup.dialogs.refill_shells import RefillShells, ExitFromShellsConfirm
from gui.impl.lobby.techtree.techtree_intro_view import TechTreeIntroWindow
from gui.impl.pub.lobby_window import LobbyWindow
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import CTRL_ENTITY_TYPE, PREBATTLE_ACTION_NAME
from gui.shared import events, g_eventBus, money
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getUserName
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.money import Currency
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getViewName, getUniqueViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shop import generateShopRentRenewProductID, showBuyGoldForRentWebOverlay
from gui.shop import getShopProductInfo
from gui.shop import makeBuyParamsByProductInfo
from gui.shop import showBuyVehicleOverlay
from helpers import dependency
from helpers.aop import pointcutable
from helpers.i18n import makeString as _ms
from items import vehicles as vehicles_core, parseIntCompactDescr, ITEM_TYPES
from nations import NAMES
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IHeroTankController, IReferralProgramController, IEpicBattleMetaGameController, IClanNotificationController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.prb_control.dispatcher import g_prbLoader
from soft_exception import SoftException
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


def showHalloweenResults(arenaUniqueID):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_BATTLE_RESULTS, getViewName(VIEW_ALIAS.EVENT_BATTLE_RESULTS, str(arenaUniqueID))), ctx={'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showRankedAwardWindow(awardsSequence, rankedInfo, notificationMgr=None):
    alias = RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD
    window = SFWindow(SFViewLoadParams(alias, getUniqueViewName(alias)), ctx={'awardsSequence': awardsSequence,
     'rankedInfo': rankedInfo}, scope=EVENT_BUS_SCOPE.LOBBY)
    notificationMgr.append(window)


def showRankedPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesPrimeTimeWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_PRIME_TIME_ALIAS), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesWelcomeBackWindow():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_WELCOME_BACK_ALIAS), ctx={}), EVENT_BUS_SCOPE.LOBBY)


def showEpicBattlesAfterBattleWindow(reusableInfo, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(EPICBATTLES_ALIASES.EPIC_BATTLES_AFTER_BATTLE_ALIAS, parent=parent), ctx={'reusableInfo': reusableInfo}), EVENT_BUS_SCOPE.LOBBY)


def showBattleRoyaleLevelUpWindow(reusableInfo, parent=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(BATTLEROYALE_ALIASES.LEVEL_UP, parent=parent), ctx={'reusableInfo': reusableInfo}), EVENT_BUS_SCOPE.LOBBY)


def showBattleRoyaleResultsView(ctx, isInBattle=False):
    if isInBattle:
        window = LobbyWindow(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BrBattleResultsViewInBattle(ctx=ctx))
        window.load()
    else:
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
def showVehicleRentRenewDialog(intCD, rentType, num, seasonType):
    if not (seasonType == GameSeasonType.EPIC and rentType == RentType.SEASON_CYCLE_RENT):
        _logger.debug('GameSeasonType %s with RentType %s is not supported', seasonType, rentType)
        return
    productID = generateShopRentRenewProductID(intCD, rentType, num, seasonType)
    productInfo = yield getShopProductInfo(productID)
    if not productInfo:
        SystemMessages.pushMessage(_ms(MESSENGER.SERVER_ERRORS_INTERNALERROR_MESSAGE), type=SystemMessages.SM_TYPE.Error)
        return
    buyParams = makeBuyParamsByProductInfo(productInfo)
    _purchaseOffer(intCD, rentType, [num], productInfo.price, seasonType, buyParams, renew=True)


@adisp.process
@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _purchaseOffer(vehicleCD, rentType, nums, price, seasonType, buyParams, renew, itemsCache=None):
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
    requestConfirmed = yield DialogsInterface.showDialog(meta=RentConfirmDialogMeta(vehicleCD, rentType, nums, price, seasonType, renew))
    if requestConfirmed:
        if mayObtainForMoney(price):
            showBuyVehicleOverlay(buyParams)
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
    from gui.impl.lobby.premacc.piggybank import PiggyBankView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.premacc.piggybank.Piggybank(), PiggyBankView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


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
    from gui.impl.lobby.instructions.booster_buy_dialog import BoosterBuyWindowView
    wrapper = FullScreenDialogWindowWrapper(BoosterBuyWindowView(battleBoosterIntCD))
    yield dialogs.showSimple(wrapper)


@async
def showBattleBoosterSellDialog(battleBoosterIntCD):
    from gui.impl.lobby.instructions.booster_sell_dialog import BoosterSellWindowView
    from gui.impl.dialogs import dialogs
    wrapper = FullScreenDialogWindowWrapper(BoosterSellWindowView(battleBoosterIntCD))
    yield dialogs.showSimple(wrapper)


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
        from gui.impl.lobby.dog_tags.dog_tags import DogTags
        uiLoader = dependency.instance(IGuiLoader)
        contentResId = R.views.lobby.dog_tags.DogTags()
        dtView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
        if dtView is not None:
            dtView.highlightComponent(compID)
        else:
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, DogTags, ScopeTemplates.LOBBY_SUB_SCOPE), highlightedComponentId=compID, makeTopView=makeTopView), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showStrongholds(url=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STRONGHOLD), ctx={'url': url}), scope=EVENT_BUS_SCOPE.LOBBY)


def openManualPage(chapterIndex):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MANUAL_CHAPTER_VIEW), ctx={'chapterIndex': chapterIndex}), EVENT_BUS_SCOPE.LOBBY)


@adisp.process
def showShop(url='', path='', params=None):
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
    url = '/'.join((node.strip('/') for node in (url, path)))
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    if app is not None and app.containerManager is not None:
        viewKey = ViewKey(VIEW_ALIAS.LOBBY_STORE)
        browserWindow = app.containerManager.getViewByKey(viewKey)
        if browserWindow is not None:
            browser = browserWindow.getBrowser()
            browser.navigate(url)
            return
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_STORE), ctx={'url': url}), scope=EVENT_BUS_SCOPE.LOBBY)
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


def showMarathonVehiclePreview(vehTypeCompDescr, itemsPack=None, title='', marathonPrefix=''):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'itemsPack': itemsPack,
     'title': title,
     'marathonPrefix': marathonPrefix}), scope=EVENT_BUS_SCOPE.LOBBY)


def showConfigurableVehiclePreview(vehTypeCompDescr, previewAlias, previewBackCb, hiddenBlocks, itemPack):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewBackCb': previewBackCb,
     'hiddenBlocks': hiddenBlocks,
     'itemsPack': itemPack}), scope=EVENT_BUS_SCOPE.LOBBY)


def showEventProgressionVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previewBackCb=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_PROGRESSION_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewBackCb': previewBackCb}), scope=EVENT_BUS_SCOPE.LOBBY)


def showVehiclePreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, vehStrCD=None, previewBackCb=None, itemsPack=None, offers=None, price=money.MONEY_UNDEFINED, oldPrice=None, title='', description=None, endTime=None, buyParams=None, vehParams=None):
    heroTankController = dependency.instance(IHeroTankController)
    heroTankCD = heroTankController.getCurrentTankCD()
    isHeroTank = heroTankCD and heroTankCD == vehTypeCompDescr
    if isHeroTank and not (itemsPack or offers or vehParams):
        goToHeroTankOnScene(vehTypeCompDescr, previewAlias)
    else:
        vehicle = dependency.instance(IItemsCache).items.getItemByCD(vehTypeCompDescr)
        if not (itemsPack or offers or vehParams) and vehicle.canPersonalTradeInBuy:
            viewAlias = VIEW_ALIAS.PERSONAL_TRADE_IN_VEHICLE_PREVIEW
        elif not (itemsPack or offers or vehParams) and vehicle.canTradeIn:
            viewAlias = VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW
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


def goToHeroTankOnScene(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR):
    import BigWorld
    from HeroTank import HeroTank
    from ClientSelectableCameraObject import ClientSelectableCameraObject
    for entity in BigWorld.entities.values():
        if entity and isinstance(entity, HeroTank):
            showHeroTankPreview(vehTypeCompDescr, previewAlias=previewAlias, previousBackAlias=None)
            ClientSelectableCameraObject.switchCamera(entity)
            break

    return


def showHeroTankPreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previousBackAlias=None):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.HERO_VEHICLE_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True,
     'previousBackAlias': previousBackAlias}), scope=EVENT_BUS_SCOPE.LOBBY)


def showHalloweenTankPreview(vehTypeCompDescr):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_STYLES_PREVIEW), ctx={'itemCD': vehTypeCompDescr,
     'previewAlias': VIEW_ALIAS.LOBBY_HANGAR,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True}), scope=EVENT_BUS_SCOPE.LOBBY)


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
    notificationMgr.append(window)


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


@adisp.process
def selectVehicleInHangar(itemCD, loadHangar=True, leaveEventMode=False):
    from CurrentVehicle import g_currentVehicle
    itemsCache = dependency.instance(IItemsCache)
    veh = itemsCache.items.getItemByCD(int(itemCD))
    if not veh.isInInventory:
        raise SoftException('Vehicle (itemCD={}) must be in inventory.'.format(itemCD))
    g_currentVehicle.selectVehicle(veh.invID)
    if leaveEventMode:
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher:
            entity = dispatcher.getEntity()
            if entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
                yield switchOutEventMode()
                entity = dispatcher.getEntity()
                if entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
                    showHangar()
                return
    if loadHangar:
        showHangar()
    return


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
    from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher:
        entity = dispatcher.getEntity()
        if entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
            visibility = HeaderMenuVisibilityState.NOTHING
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
    showBrowserOverlayView(url, alias=VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW)
    return


@adisp.process
def showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB, params=None, callbackOnLoad=None, webHandlers=None, forcedSkipEscape=False):
    if url:
        url = yield URLMacros().parse(url, params=params)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias), ctx={'url': url,
         'allowRightClick': False,
         'callbackOnLoad': callbackOnLoad,
         'webHandlers': webHandlers,
         'forcedSkipEscape': forcedSkipEscape}), EVENT_BUS_SCOPE.LOBBY)


def showSeniorityRewardWindow():
    from gui.impl.lobby.seniority_awards.seniority_reward_view import SeniorityRewardWindow
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.seniority_awards.seniority_reward_view.SeniorityRewardView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        window = SeniorityRewardWindow(contentResId)
        window.load()
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
    notificationMgr.append(window)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showSeniorityRewardAwardWindow(qID, data, notificationMgr=None):
    from gui.impl.lobby.seniority_awards.seniority_reward_award_view import SeniorityRewardAwardWindow
    window = SeniorityRewardAwardWindow(qID, data)
    notificationMgr.append(window)


def showBattlePassAwardsWindow(bonuses, data):
    from gui.impl.lobby.battle_pass.battle_pass_awards_view import BattlePassAwardWindow
    wndFlags = WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN
    window = BattlePassAwardWindow(bonuses, data, wndFlags=wndFlags)
    window.load()


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showBattlePassVehicleAwardWindow(data, notificationMgr=None):
    from gui.impl.lobby.battle_pass.battle_pass_vehicle_award_view import BattlePassVehicleAwardWindow
    window = BattlePassVehicleAwardWindow(data)
    notificationMgr.append(window)


def showBattleVotingResultWindow(isOverlay=False, parent=None):
    from gui.impl.lobby.battle_pass.battle_pass_voting_result_view import BattlePassVotingResultWindow
    window = BattlePassVotingResultWindow(isOverlay, parent)
    window.load()


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


def showBattlePassOnboardingWindow(parent=None):
    from gui.impl.lobby.battle_pass.battle_pass_onboarding_view import BattlePassOnboardingWindow
    window = BattlePassOnboardingWindow(parent)
    window.load()


def showStylePreview(vehCD, style, styleDescr, backCallback, backBtnDescrLabel=''):
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STYLE_PREVIEW), ctx={'itemCD': vehCD,
     'style': style,
     'styleDescr': styleDescr,
     'backCallback': backCallback,
     'backBtnDescrLabel': backBtnDescrLabel}), scope=EVENT_BUS_SCOPE.LOBBY)


def showTechTreeIntro(parent=None, blueprints=None):
    window = TechTreeIntroWindow(parent=parent, convertedBlueprints=blueprints if blueprints is not None else {})
    window.load()
    return


def showRankedSeasonCompleteView(ctx, useQueue=False):
    params = SFViewLoadParams(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE)
    findAndLoadWindow(useQueue, SFWindow, params, EVENT_BUS_SCOPE.LOBBY, ctx=ctx)


def showRankedYearAwardWindow(rawAwards, points, useQueue=False):
    from gui.impl.lobby.ranked.ranked_year_award_view import RankedYearAwardWindow
    findAndLoadWindow(useQueue, RankedYearAwardWindow, rawAwards, points)


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
        notificationMgr.append(newWindow)
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
def showResSimpleDialog(resources, icon, formattedMessage):
    from gui.impl.dialogs import dialogs
    from gui.impl.dialogs.builders import ResSimpleDialogBuilder
    builder = ResSimpleDialogBuilder()
    builder.setMessagesAndButtons(resources)
    builder.setIcon(icon)
    builder.setFormattedMessage(formattedMessage)
    result = yield await(dialogs.showSimple(builder.build()))
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
def showFrontlineExchangePrestigePoints(ctx):
    from gui.impl.dialogs.builders import InfoDialogBuilder
    from gui.impl.dialogs import dialogs
    from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArgs
    from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import exchangePrestigePoints
    from gui.server_events.formatters import formatGoldPrice, formatCrystalPrice
    __ctrl = dependency.instance(IEpicBattleMetaGameController)
    prestigePoints = ctx.get('prestige_points', 0)
    gold = ctx.get('gold', 1) * prestigePoints
    crystals = ctx.get('crystal', 1) * prestigePoints
    canBuyVehs = ctx.get('canBuy')
    if canBuyVehs:
        dialogParams = R.strings.dialogs.frontline.dialogPrestigePointsConvert
    else:
        dialogParams = R.strings.dialogs.frontline.dialogPrestigePointsConvert.haveAllTank
    builder = InfoDialogBuilder()
    builder.setMessagesAndButtons(dialogParams)
    builder.setMessageArgs(fmtArgs=[FmtArgs(str(prestigePoints), 'points', R.styles.NeutralTextStyle()), FmtArgs(formatGoldPrice(gold), 'gold', R.styles.GoldTextStyle()), FmtArgs(formatCrystalPrice(crystals), 'bons', R.styles.CrystalTextStyle())])
    result = yield await(dialogs.showSimple(builder.build()))
    if result:
        exchangePrestigePoints()


@async
def showDialog(dialog, callback):
    from gui.impl.dialogs import dialogs
    isOk = yield await(dialogs.showSimple(dialog))
    callback((isOk, {}))


@async
def showOptDeviceCommonWindowDialog(wrappedViewClass, deviceDescr):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(compDescr=deviceDescr, layoutID=R.views.lobby.demountkit.CommonWindow(), wrappedViewClass=wrappedViewClass))
    if result.busy:
        raise AsyncReturn((False, {}))
    else:
        isOk, _ = result.result
        raise AsyncReturn((isOk, {}))


@async
def showOptionalDeviceDestroy(deviceDescr, callback):
    result = yield await(showOptDeviceCommonWindowDialog(DestroyOpDevDialog, deviceDescr))
    callback(result)


@async
def showOptionalDeviceInstall(deviceDescr, callback):
    result = yield await(showOptDeviceCommonWindowDialog(InstallOpDevDialog, deviceDescr))
    callback(result)


@async
def showOptionalDeviceDemount(deviceDescr, callback, forFitting=False):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(compDescr=deviceDescr, forFitting=forFitting, layoutID=R.views.lobby.demountkit.DemountWindow(), wrappedViewClass=DemountOpDevDialog))
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
    result = yield await(dialogs.showSingleDialogWithResultData(compDescr=deviceDescr, forFitting=forFitting, layoutID=R.views.lobby.demountkit.CommonWindow(), wrappedViewClass=DemountOpDevSinglePriceDialog))
    if result.busy:
        callback((False, {}))
    else:
        isOK, data = result.result
        if data.get('openDemountSelectorWindow', False):
            showOptionalDeviceDemount(deviceDescr, callback, forFitting=forFitting)
        else:
            callback((isOK, data))


@async
def showOptionalDeviceBuyAndInstall(deviceDescr, callback):
    result = yield await(showOptDeviceCommonWindowDialog(BuyAndInstallOpDevDialog, deviceDescr))
    callback(result)


@async
def showOptionalDeviceBuyAndStorage(deviceDescr, callback):
    result = yield await(showOptDeviceCommonWindowDialog(BuyAndStorageOpDevDialog, deviceDescr))
    callback(result)


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
    dialogBuilder = makeOfferGiftDialog(offerID, giftID, cdnTitle)
    yield showDialog(dialogBuilder.build(), callback)


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
    notificationMgr.append(window)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showProgressionRequiredStyleUnlockedWindow(vehicleCD, notificationMgr=None):
    from gui.impl.lobby.customization.style_unlocked_view.style_unlocked_view import StyleUnlockedWindow
    window = StyleUnlockedWindow(vehicleCD)
    notificationMgr.append(window)


def showProgressiveItemsView(itemIntCD=None):
    from gui.impl.lobby.customization.progressive_items_view.progressive_items_view import ProgressiveItemsView
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION))
    if view is None:
        _logger.error('ProgressiveItemsView shall be created only from customization')
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.customization.progressive_items_view.ProgressiveItemsView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentResId, viewClass=ProgressiveItemsView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), view, wsFlags=ViewFlags.LOBBY_TOP_SUB_VIEW, itemIntCD=itemIntCD), scope=EVENT_BUS_SCOPE.LOBBY)
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
def showTankSetupConfirmDialog(items, vehInvID=None, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=TankSetupConfirmDialog, items=items, vehInvID=vehInvID, startState=startState, parent=parent))
    raise AsyncReturn(result)


@async
def showTankSetupExitConfirmDialog(items, vehInvID=None, startState=None, fromSection=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=TankSetupExitConfirmDialog, items=items, vehInvID=vehInvID, startState=startState, fromSection=fromSection, parent=parent))
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
    from gui.impl.dialogs import dialogs
    result = yield await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=BattleAbilitiesSetupConfirm, items=items, withInstall=withInstall, parent=parent))
    raise AsyncReturn(result)


@adisp.async
@adisp.process
def switchOutEventMode(callback=None):
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher:
        entity = dispatcher.getEntity()
        if entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
            yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
    if callable(callback):
        callback(False)
    return


def showCongratulationWindow(packType):
    from gui.impl.lobby.halloween.congratulation_view import CongratulationView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.lobby.halloween.CongratulationView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        window = LobbyWindow(WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CongratulationView(contentResId, packType=packType))
        window.load()
    return


@adisp.async
@adisp.process
def hideTopWindows(callback=None):
    from gui.Scaleform.framework.entities.View import View
    from frameworks.wulf import WindowLayer
    lobbyContext = dependency.instance(ILobbyContext)
    windowsManager = dependency.instance(IGuiLoader).windowsManager
    yield lobbyContext.isHeaderNavigationPossible()

    def predicateTopWindows(window):
        content = window.content
        return False if content is None else isinstance(content, View) and content.layer in (WindowLayer.TOP_WINDOW,)

    for window in windowsManager.findWindows(predicateTopWindows):
        if hasattr(window, 'destroyWindow'):
            window.destroyWindow()
        if hasattr(window, 'destroy'):
            window.destroy()

    if callback is not None:
        callback(None)
    return
