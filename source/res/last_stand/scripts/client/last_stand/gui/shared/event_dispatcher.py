# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/event_dispatcher.py
from frameworks.wulf import WindowLayer
from BWUtil import AsyncReturn
from gui import GUI_SETTINGS
from gui.lootbox_system.base.common import ViewID, Views
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.common.fade_manager import UseFading
from gui.impl.gen import R
from gui.Scaleform.framework import ScopeTemplates
from frameworks.wulf import WindowFlags
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.event_dispatcher import showShop, _getModuleInfoViewName, showBrowserOverlayView, findAndLoadWindow, selectVehicleInHangar
from last_stand.gui.ls_gui_constants import LS_INFO_PAGE_KEY, LS_INTRO_VIDEO_KEY
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.impl import INotificationWindowController
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
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


def isViewLoaded(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    return True if not uiLoader or not uiLoader.windowsManager or uiLoader.windowsManager.getViewByLayoutID(layoutID) else False


@UseFading(layer=WindowLayer.OVERLAY, waitForLayoutReady=R.views.last_stand.mono.lobby.hangar())
def showHangar(artefactID=None):
    from last_stand.gui.impl.lobby.hangar_view import HangarView
    layoutID = R.views.last_stand.mono.lobby.hangar()
    if isViewLoaded(layoutID=layoutID):
        return
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, HangarView, ScopeTemplates.LOBBY_SUB_SCOPE), artefactID=artefactID), scope=EVENT_BUS_SCOPE.LOBBY)


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
    from ClientSelectableCameraObject import ClientSelectableCameraObject
    ClientSelectableCameraObject.switchCamera()
    viewAlias = LAST_STAND_HANGAR_ALIASES.LS_VEHICLE_PREVIEW
    app = dependency.instance(IAppLoader).getApp()
    view = app.containerManager.getViewByKey(ViewKey(viewAlias))
    if view is not None:
        view.destroy()
    kwargs.update({'isHiddenMenu': True})
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(viewAlias), ctx=kwargs), EVENT_BUS_SCOPE.LOBBY)
    return


@UseFading(layer=WindowLayer.OVERLAY, waitForLayoutReady=R.views.last_stand.mono.lobby.reward_path_view())
def showRewardPathView(selectedArtefactID=None):
    from last_stand.gui.impl.lobby.reward_path_view import RewardPathView
    layoutID = R.views.last_stand.mono.lobby.reward_path_view()
    if isViewLoaded(layoutID=layoutID):
        return
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, RewardPathView, ScopeTemplates.LOBBY_SUB_SCOPE), selectedArtefactID=selectedArtefactID), scope=EVENT_BUS_SCOPE.LOBBY)


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


def showIntroVideo():
    url = GUI_SETTINGS.lookup(LS_INTRO_VIDEO_KEY)
    showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


def showInfoPage():
    url = GUI_SETTINGS.lookup(LS_INFO_PAGE_KEY)
    showBrowserOverlayView(url, LAST_STAND_HANGAR_ALIASES.LS_BROWSER, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


def showHangarAmmunitionSetupView(*args, **kwargs):
    from last_stand.gui.impl.lobby.hangar_ammunition_setup_view import LSHangarAmmunitionSetupView
    layoutID = R.views.last_stand.mono.lobby.ammunition_setup()
    if isViewLoaded(layoutID=layoutID):
        return
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, LSHangarAmmunitionSetupView, ScopeTemplates.LOBBY_SUB_SCOPE), *args, **kwargs), scope=EVENT_BUS_SCOPE.LOBBY)


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showBattleResult(arenaUniqueID, notificationsMgr=None):
    from last_stand.gui.impl.lobby.battle_result_view import BattleResultView as BattleResultViewInLobby
    layoutID = R.views.last_stand.mono.lobby.battle_result_view()
    if isViewLoaded(layoutID=layoutID):
        return
    ctx = {'arenaUniqueID': arenaUniqueID}
    view = BattleResultViewInLobby(layoutID, ctx)
    window = LobbyNotificationWindow(WindowFlags.WINDOW_FULLSCREEN, content=view, layer=WindowLayer.FULLSCREEN_WINDOW)
    notificationsMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(lootBoxCtrl=ILootBoxSystemController)
def showLootBoxMainView(eventName, lootBoxCtrl=None):
    if lootBoxCtrl.isAvailable(eventName):
        Views.load(ViewID.MAIN, eventName=eventName)


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showLootBoxMainViewInQueue(eventName, notificationsMgr=None):
    notificationsMgr.append(EventNotificationCommand(NotificationEvent(showLootBoxMainView, eventName)))


def showLSShopBundle(bundleUrl):
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
