# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/event_dispatcher.py
from CurrentVehicle import HeroTankPreviewAppearance
from frameworks.wulf import WindowLayer
from BWUtil import AsyncReturn
from gui import GUI_SETTINGS
from gui.lootbox_system.base.common import ViewID, Views
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.common.fade_manager import UseFading
from gui.impl.gen import R
from frameworks.wulf import WindowFlags
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.event_dispatcher import showShop, _getModuleInfoViewName, showBrowserOverlayView, findAndLoadWindow, selectVehicleInHangar
from gui.shared.lock_overlays import lockNotificationManager
from last_stand.gui.ls_gui_constants import LS_INFO_PAGE_KEY, LS_INTRO_VIDEO_KEY
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.impl import INotificationWindowController
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getSettings
from last_stand.gui.impl.lobby.tank_setup.dialogs.confirm_dialog import LSTankSetupConfirmDialog
from helpers import dependency
from gui.impl.pub.notification_commands import EventNotificationCommand, NotificationEvent, WindowNotificationCommand
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from wg_async import wg_await, wg_async
from last_stand.gui.scaleform.genConsts.LAST_STAND_HANGAR_ALIASES import LAST_STAND_HANGAR_ALIASES

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getUrl(urlName=None, url=None, lobbyContext=None):
    hostUrl = lobbyContext.getServerSettings().shop.hostUrl
    return hostUrl + url if url else hostUrl + ('' if urlName is None else GUI_SETTINGS.lookup('lsShop').get(urlName))


def getLoadedViewByLayoutID(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    return uiLoader.windowsManager.getViewByLayoutID(layoutID) if uiLoader and uiLoader.windowsManager else None


def isViewLoaded(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    return True if not uiLoader or not uiLoader.windowsManager or uiLoader.windowsManager.getViewByLayoutID(layoutID) else False


def showHangar():
    from last_stand.gui.impl.lobby.states import LastStandHangarState
    LastStandHangarState.goTo()


def isHangarLoaded():
    return isViewLoaded(R.views.last_stand.mono.lobby.hangar())


def showMetaIntroView(forceOpen=True, parent=None):
    from last_stand.gui.impl.lobby.meta_intro_view import MetaIntroWindow
    layoutID = R.views.last_stand.mono.lobby.meta_intro()
    isShowed = getSettings(AccountSettingsKeys.META_INTRO_VIEW_SHOWED)
    if isViewLoaded(layoutID) or isShowed and not forceOpen:
        return
    wnd = MetaIntroWindow(parent)
    wnd.load()


def showVehiclePreview(**kwargs):
    kwargs.update({'isHiddenMenu': True})
    from last_stand.gui.impl.lobby.states import LastStandVehiclePreviewState
    LastStandVehiclePreviewState.goTo(ctx=kwargs)


def showHeroTankPreview(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previousBackAlias=None, previewBackCb=None, hangarVehicleCD=None, backOutfit=None, backBtnLabel='', isHiddenMenu=True, isKingReward=False):
    ctx = {'itemCD': vehTypeCompDescr,
     'previewAlias': previewAlias,
     'previewAppearance': HeroTankPreviewAppearance(),
     'isHeroTank': True,
     'previousBackAlias': previousBackAlias,
     'previewBackCb': previewBackCb,
     'hangarVehicleCD': hangarVehicleCD,
     'backOutfit': backOutfit,
     'backBtnLabel': backBtnLabel,
     'isHiddenMenu': isHiddenMenu,
     'isKingReward': isKingReward}
    from last_stand.gui.impl.lobby.states import LastStandHeroTankPreviewState
    LastStandHeroTankPreviewState.goTo(ctx=ctx)


def showRewardPathView():
    from last_stand.gui.impl.lobby.states import LastStandRewardPathState
    LastStandRewardPathState.goTo()


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showPromoWindowView(forceOpen=False, notificationsMgr=None):
    from last_stand.gui.impl.lobby.promo_window_view import PromoWindow
    layoutID = R.views.last_stand.mono.lobby.promo_view()
    isShowed = getSettings(AccountSettingsKeys.PROMO_SCREEN_SHOWED)
    if isViewLoaded(layoutID=layoutID) or isShowed and not forceOpen:
        return
    window = PromoWindow(layoutID)
    notificationsMgr.append(WindowNotificationCommand(window))


def showDifficultyView(level, showDailyWidget=False, useQueue=False):
    from last_stand.gui.impl.lobby.difficulty_window_view import DifficultyWindow
    layoutID = R.views.last_stand.mono.lobby.difficulty_congratulation_view()
    findAndLoadWindow(useQueue, DifficultyWindow, layoutID, level, showDailyWidget)


def showKingRewardCongratsView(useQueue=False):
    from last_stand.gui.impl.lobby.king_reward_congrats_view import KingRewardCongratsWindow
    layoutID = R.views.last_stand.mono.lobby.king_reward_view()
    findAndLoadWindow(useQueue, KingRewardCongratsWindow, layoutID)


def showDecryptWindowView(artefactID, useQueue=False, isReward=False):
    from last_stand.gui.impl.lobby.decrypt_view import DecryptWindow
    findAndLoadWindow(useQueue, DecryptWindow, artefactID, isReward)


@dependency.replace_none_kwargs(lsController=ILSController)
def showIntroVideo(lsController=None):
    if not lsController.isIntroVideoEnabled():
        return
    url = GUI_SETTINGS.lookup(LS_INTRO_VIDEO_KEY)
    showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


def showInfoPage():
    url = GUI_SETTINGS.lookup(LS_INFO_PAGE_KEY)
    showBrowserOverlayView(url, LAST_STAND_HANGAR_ALIASES.LS_BROWSER, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


def showHangarAmmunitionSetupView(**kwargs):
    from last_stand.gui.impl.lobby.states import LastStandAmmunitionSetupLoadout
    LastStandAmmunitionSetupLoadout.goTo(**kwargs)


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showBattleResult(arenaUniqueID, notificationsMgr=None):
    from last_stand.gui.impl.lobby.battle_result_view import BattleResultView as BattleResultViewInLobby
    layoutID = R.views.last_stand.mono.lobby.battle_result_view()
    if isViewLoaded(layoutID=layoutID):
        return
    ctx = {'arenaUniqueID': arenaUniqueID}
    view = BattleResultViewInLobby(layoutID, ctx)
    window = LobbyNotificationWindow(WindowFlags.WINDOW_FULLSCREEN, content=view, layer=WindowLayer.FULLSCREEN_WINDOW)
    lockNotificationManager(True, source=layoutID, postponeActive=True)
    notificationsMgr.append(WindowNotificationCommand(window))
    lockNotificationManager(False, source=layoutID, releasePostponed=True)


@dependency.replace_none_kwargs(lootBoxCtrl=ILootBoxSystemController)
def showLootBoxMainView(eventName, lootBoxCtrl=None):
    if lootBoxCtrl.isAvailable(eventName):
        Views.load(ViewID.MAIN, eventName=eventName)


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showLootBoxMainViewInQueue(eventName, notificationsMgr=None):
    notificationsMgr.append(EventNotificationCommand(NotificationEvent(showLootBoxMainView, eventName)))


@dependency.replace_none_kwargs(lsArtefactsController=ILSArtefactsController)
def showLSShopAll(lsArtefactsController=None):
    lsArtefactsController.resetSelectedArtefactID()
    showShop(_getUrl('lsShopAll'))


@dependency.replace_none_kwargs(lsArtefactsController=ILSArtefactsController)
def showLSShopBundle(bundleUrl, lsArtefactsController=None):
    lsArtefactsController.resetSelectedArtefactID()
    showShop(_getUrl(url=bundleUrl))


def showBundleWindow(artefactID=''):
    from last_stand.gui.impl.lobby.bundle_view import BundleWindow
    layoutID = R.views.last_stand.mono.lobby.bundle_view()
    if isViewLoaded(layoutID=layoutID):
        return
    wnd = BundleWindow(layoutID, artefactID)
    wnd.load()
    return wnd


@wg_async
def showTankSetupConfirmDialog(items, vehicle=None, startState=None, parent=None):
    from gui.impl.dialogs import dialogs
    result = yield wg_await(dialogs.showSingleDialogWithResultData(layoutID=R.views.lobby.tanksetup.dialogs.Confirm(), wrappedViewClass=LSTankSetupConfirmDialog, items=items, vehicle=vehicle, startState=startState, parent=parent))
    raise AsyncReturn(result)


def showModuleInfo(itemCD, vehicleDescr):
    itemCD = int(itemCD)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(LAST_STAND_HANGAR_ALIASES.LS_MODULE_INFO, _getModuleInfoViewName(itemCD, vehicleDescr)), ctx={'moduleCompactDescr': itemCD,
     'vehicleDescr': vehicleDescr}), EVENT_BUS_SCOPE.LOBBY)


def closeViewsByID(layoutIDs):
    uiLoader = dependency.instance(IGuiLoader)
    if not uiLoader or not uiLoader.windowsManager:
        return
    for layoutID in layoutIDs:
        view = uiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view:
            view.destroyWindow()


@UseFading(layer=WindowLayer.OVERLAY)
def selectVehicleInHangarWithFade(itemCD, loadHangar=True):
    selectVehicleInHangar(itemCD, loadHangar)


def showAttachmentRewardWindow(element, isFirstEntry, useQueue=True):
    from last_stand.gui.impl.lobby.attachment_reward_view import AttachmentRewardWindow
    findAndLoadWindow(useQueue, AttachmentRewardWindow, element, isFirstEntry)
