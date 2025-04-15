# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/event_dispatcher.py
import typing
import BigWorld
from adisp import adisp_async, adisp_process
from wg_async import wg_async, wg_await
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.lobby.mode_selector.items.base_item import getInfoPageKey
from gui.impl.common.fade_manager import waitWindowLoading
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import isViewLoaded, _killOldView, showHeroTankPreview, showShop, showBrowserOverlayView
from gui.Scaleform.daapi.view.lobby.vehicle_preview.shared import tryGetExternalAvailablePreviewAlias
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getHB24CategoryUrl
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME
from skeletons.gui.impl import INotificationWindowController
from gui.impl.pub.notification_commands import EventNotificationCommand, NotificationEvent
from skeletons.gui.impl import IGuiLoader
from gui.shared.lock_overlays import lockNotificationManager
from historical_battles.gui.impl.lobby import HB_LOCK_SOURCE_NAME
import logging
if typing.TYPE_CHECKING:
    from typing import Tuple, Type
    from frameworks.wulf import View
_logger = logging.getLogger(__name__)
MAIN_PRIZE_LOADING_DELAY = 0.3

@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController)
def showHBBattleResult(arenaUniqueID, notificationsMgr=None):
    notificationsMgr.append(EventNotificationCommand(NotificationEvent(method=showHistoricalBattleResultView, arenaUniqueID=arenaUniqueID)))


def showHistoricalBattleResultView(arenaUniqueID):
    lockNotificationManager(True, source=HB_LOCK_SOURCE_NAME)
    from historical_battles.gui.impl.lobby.battle_result_view import BattleResultView
    uiLoader = dependency.instance(IGuiLoader)
    contentResId = R.views.historical_battles.lobby.BattleResultView()
    battleResultView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
    if battleResultView is not None:
        if battleResultView.arenaUniqueID == arenaUniqueID:
            return
        battleResultView.destroyWindow()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(BattleResultView.layoutID, BattleResultView, ScopeTemplates.LOBBY_TOP_SUB_SCOPE), arenaUniqueID=arenaUniqueID), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@adisp_async
@adisp_process
def showCongratsMainRewardView(forGold, showHangarOnClose=False, callback=None):
    yield lambda callback: callback(None)
    from historical_battles.gui.impl.lobby.congrats_main_reward_view import CongratsMainRewardWindow
    if _killOldView(R.views.historical_battles.lobby.CongratsMainRewardView()):
        return
    else:
        yield waitWindowLoading(CongratsMainRewardWindow(forGold, showHangarOnClose))
        callback(None)
        return


def showHistoricalBattleQueueView():
    from historical_battles.gui.impl.lobby.pre_battle_queue_view import PreBattleQueueView
    layout = R.views.historical_battles.lobby.PreBattleQueueView()
    hbCtrl = dependency.instance(IGameEventController)
    if hbCtrl:
        hbCtrl.onShowBattleQueueView()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layout, PreBattleQueueView, ScopeTemplates.DEFAULT_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def showShopView():
    showShop(getHB24CategoryUrl())


@wg_async
def showCoinsExchangeWindow():
    from historical_battles.gui.impl.lobby.shop_views.exchange_coins_view import ExchangeCoinsView
    yield wg_await(dialogs.show(FullScreenDialogWindowWrapper(ExchangeCoinsView(), layer=WindowLayer.FULLSCREEN_WINDOW)))


def showOrdersInfoWindow():
    from historical_battles.gui.impl.lobby.order_info_view import HBOrderInfoView
    layout = R.views.historical_battles.lobby.OrderInfoView()
    if isViewLoaded(layout):
        return
    wnd = HBOrderInfoView(layout)
    wnd.load()


def showInfoWindow(infoViewSettings):
    layout, view = infoViewSettings
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layout, view, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


def goToHBHeroTankOnScene(vehTypeCompDescr, previewAlias=VIEW_ALIAS.LOBBY_HANGAR, previewBackCb=None, previousBackAlias=None, hangarVehicleCD=None, immediate=False):
    from HBHeroTank import HBHeroTank
    from ClientSelectableCameraObject import ClientSelectableCameraObject
    for entity in BigWorld.entities.values():
        if entity and isinstance(entity, HBHeroTank):
            descriptor = entity.typeDescriptor
            if descriptor:
                extViewAlias = tryGetExternalAvailablePreviewAlias()
                showHeroTankPreview(vehTypeCompDescr, viewAlias=extViewAlias or None, previewAlias=previewAlias, previewBackCb=previewBackCb, previousBackAlias=previousBackAlias, hangarVehicleCD=hangarVehicleCD)
                ClientSelectableCameraObject.switchCamera(entity, immediate=immediate)
                break

    return


def showHBProgressionView(frontId=None):
    from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.hb_meta_view_model import TabId
    from historical_battles.gui.impl.lobby.views.hb_meta_view import HBMetaView
    viewRes = R.views.historical_battles.lobby.HBMetaView()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(viewRes, HBMetaView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), TabId.PROGRESS, frontId), scope=EVENT_BUS_SCOPE.LOBBY)


def showHBOrderView():
    from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.hb_meta_view_model import TabId
    from historical_battles.gui.impl.lobby.views.hb_meta_view import HBMetaView
    viewRes = R.views.historical_battles.lobby.HBMetaView()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(viewRes, HBMetaView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), TabId.ORDER), scope=EVENT_BUS_SCOPE.LOBBY)


def showHBDivisionsView():
    from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.hb_meta_view_model import TabId
    from historical_battles.gui.impl.lobby.views.hb_meta_view import HBMetaView
    viewRes = R.views.historical_battles.lobby.HBMetaView()
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(viewRes, HBMetaView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), TabId.DIVISION), scope=EVENT_BUS_SCOPE.LOBBY)


@wg_async
def showHBFairplayDialog(data=None, callback=None):
    from historical_battles.gui.impl.lobby.fairplayWindow import FairPlayWindow
    result = yield wg_await(dialogs.showSingleDialogWithResultData(data=data or {}, layoutID=FairPlayWindow.LAYOUT_ID, wrappedViewClass=FairPlayWindow, layer=WindowLayer.WINDOW))
    if result.busy:
        if callback is not None:
            callback(False)
    else:
        isOK, _ = result.result
        if callback is not None:
            callback(isOK)
    return


@wg_async
def showHBFairplayWarningDialog(reason='', callback=None):
    from historical_battles.gui.impl.lobby.fairplayWarningWindow import FairPlayWarningWindow
    result = yield wg_await(dialogs.showSingleDialogWithResultData(reason=reason, layoutID=FairPlayWarningWindow.LAYOUT_ID, wrappedViewClass=FairPlayWarningWindow, layer=WindowLayer.WINDOW))
    if result.busy:
        if callback is not None:
            callback(False)
    else:
        isOK, _ = result.result
        if callback is not None:
            callback(isOK)
    return


def showAwardsView(stage, closeCallback=None):
    from historical_battles.gui.impl.lobby.views.battle_quest_awards_view import BattleQuestAwardsViewWindow
    BattleQuestAwardsViewWindow(stage, closeCallback).load()


def showInfoPage():
    url = GUI_SETTINGS.lookup(getInfoPageKey(PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES))
    showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


def showProgressionVideo(videoName, parent):
    from historical_battles.gui.impl.lobby.progression_video_view import ProgressionVideoWindow
    window = ProgressionVideoWindow(videoName, parent)
    window.load()
