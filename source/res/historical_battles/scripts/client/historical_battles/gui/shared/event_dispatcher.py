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
import logging
if typing.TYPE_CHECKING:
    from typing import Tuple, Type
    from frameworks.wulf import View
_logger = logging.getLogger(__name__)
MAIN_PRIZE_LOADING_DELAY = 0.3

def openBuyBoosterBundleWindow():
    from historical_battles.gui.impl.lobby.shop_views.boosters_shop_view import HBBoosterShop
    layout = R.views.historical_battles.lobby.BoostersShopView()
    if isViewLoaded(layout):
        return
    wnd = HBBoosterShop(layout)
    wnd.load()


def showHistoricalBattleResultView(arenaUniqueID):
    from historical_battles.gui.impl.lobby.battle_result_view import BattleResultView
    _killOldView(BattleResultView.layoutID)
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(BattleResultView.layoutID, BattleResultView, ScopeTemplates.LOBBY_TOP_SUB_SCOPE), arenaUniqueID=arenaUniqueID), scope=EVENT_BUS_SCOPE.LOBBY)


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


def showHBHangar():
    layoutID = R.views.historical_battles.lobby.HangarView()
    if isViewLoaded(layoutID):
        return True
    geCtrl = dependency.instance(IGameEventController)
    if geCtrl.isHistoricalBattlesMode():
        g_eventBus.handleEvent(events.DestroyViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        from historical_battles.gui.impl.lobby.hangar_view import HangarView
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, HangarView, ScopeTemplates.LOBBY_TOP_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
        return True
    return False


@wg_async
def showCoinsExchangeWindow():
    from historical_battles.gui.impl.lobby.shop_views.exchange_coins_view import ExchangeCoinsView
    yield wg_await(dialogs.show(FullScreenDialogWindowWrapper(ExchangeCoinsView(), layer=WindowLayer.FULLSCREEN_WINDOW)))


def showOrdersX15InfoWindow():
    from historical_battles.gui.impl.lobby.order_info_view import HBOrderInfoView
    layout = R.views.historical_battles.lobby.InfoViews.OrderInfoX15View()
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


def showHBProgressionView():
    from historical_battles.gui.impl.lobby.views.progression_main_view import ProgressionMainView
    viewRes = R.views.historical_battles.lobby.ProgressionMainView()
    view = ProgressionMainView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(viewRes, view, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)


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


def showAwardsView(stage):
    from historical_battles.gui.impl.lobby.views.battle_quest_awards_view import BattleQuestAwardsViewWindow
    BattleQuestAwardsViewWindow(stage).load()


def showInfoPage():
    url = GUI_SETTINGS.lookup(getInfoPageKey(PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES))
    showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))
