# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/shared/event_dispatcher.py
import logging
import BigWorld
import HWAccountSettings
import adisp
from frameworks.wulf import WindowLayer, WindowFlags
from gui import GUI_SETTINGS, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub.fade_manager import waitGuiImplViewLoading, useDefaultFade, waitWindowLoading
from halloween.hw_constants import AccountSettingsKeys, INVALID_PHASE_INDEX
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.shared.event_dispatcher import isViewLoaded, showBrowserOverlayView, findAndLoadWindow
from helpers import dependency
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.game_control import IAwardController
from gui.shared.event_dispatcher import showShop
from gui.shared.notifications import NotificationPriorityLevel
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getHalloween2023ShopUrl
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.pub.notification_commands import WindowNotificationCommand
from halloween.gui.game_control.award_handlers import HWBattleQuestsRewardHandler
_logger = logging.getLogger(__name__)
INFO_PAGE_KEY = 'infoPageEvent'

@useDefaultFade(layer=WindowLayer.SERVICE_LAYOUT)
@adisp.adisp_async
@adisp.adisp_process
def loadGuiImplViewWithAnimation(layoutID, viewClass, scope=ScopeTemplates.LOBBY_SUB_SCOPE, callback=None, delay=None, *args, **kwargs):
    yield lambda callback: callback(None)
    if isViewLoaded(layoutID):
        callback(None)
        return
    else:
        yield waitGuiImplViewLoading(GuiImplViewLoadParams(layoutID, viewClass, scope), delay=delay, *args, **kwargs)
        callback(None)
        return


def showRewardScreenWindow(data, bonuses, useQueue=False):
    from halloween.gui.impl.lobby.reward_screen_view import RewardScreenWindow
    findAndLoadWindow(useQueue, RewardScreenWindow, data, bonuses)


def showMetaView(selectedPhase=INVALID_PHASE_INDEX):
    from halloween.gui.impl.lobby.meta_view import MetaView
    layoutID = R.views.halloween.lobby.MetaView()
    if isViewLoaded(layoutID):
        return
    loadGuiImplViewWithAnimation(layoutID, MetaView, scope=ScopeTemplates.LOBBY_SUB_SCOPE, selectedPhase=selectedPhase)


def showDailyBonuseView(forceOpen=True):
    from halloween.gui.impl.lobby.daily_and_bonus_quest_view import DailyAndBonusQuestWindow
    layoutID = R.views.halloween.lobby.DailyAndBonusQuestView()
    if isViewLoaded(layoutID) and not forceOpen:
        return
    wnd = DailyAndBonusQuestWindow(layoutID)
    wnd.load()


def showMetaIntroView(forceOpen=True, onViewLoaded=None, onViewClosed=None, parent=None):
    from halloween.gui.impl.lobby.meta_intro_view import MetaIntroWindow
    layoutID = R.views.halloween.lobby.MetaIntroView()
    isShowed = HWAccountSettings.getSettings(AccountSettingsKeys.META_INTRO_VIEW_SHOWED)
    if isViewLoaded(layoutID) or isShowed and not forceOpen:
        return
    wnd = MetaIntroWindow(layoutID, onViewLoaded, onViewClosed, parent)
    wnd.load()


@adisp.adisp_async
@adisp.adisp_process
def showPreviewView(selectedPhase=0, callback=None, parent=None, onClose=None):
    yield lambda callback: callback(None)
    from halloween.gui.impl.lobby.preview_view import PreviewWindow
    if isViewLoaded(R.views.halloween.lobby.PreviewView()):
        return
    else:
        yield waitWindowLoading(PreviewWindow(selectedPhase=selectedPhase, onClose=onClose, parent=parent))
        callback(None)
        return


def showInfoPage():
    url = GUI_SETTINGS.lookup(INFO_PAGE_KEY)
    showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


def _showErrorMessagePlayerInQueue():
    SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.queue.isInQueue()), type=SystemMessages.SM_TYPE.Error, priority=NotificationPriorityLevel.MEDIUM)


@dependency.replace_none_kwargs(notificationsMgr=INotificationWindowController, awardCtrl=IAwardController)
def showBattleHalloweenResultsView(ctx, notificationsMgr=None, awardCtrl=None):
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher is None:
        _logger.error('Prebattle dispatcher is not defined')
        return
    else:
        entity = dispatcher.getEntity()
        if entity.isInQueue():
            BigWorld.callback(0, _showErrorMessagePlayerInQueue)
            return
        from halloween.gui.impl.lobby.battle_result_view import BattleResultView as BattleResultViewInLobby
        uiLoader = dependency.instance(IGuiLoader)
        layoutID = R.views.halloween.lobby.BattleResultView()
        battleResultView = uiLoader.windowsManager.getViewByLayoutID(layoutID)
        if battleResultView is not None:
            if battleResultView.arenaUniqueID == ctx.get('arenaUniqueID', -1):
                return
            battleResultView.destroyWindow()
        view = BattleResultViewInLobby(layoutID, ctx)
        window = LobbyNotificationWindow(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=view, layer=WindowLayer.TOP_WINDOW)
        awardCtrl.handlePostponedByHandler(HWBattleQuestsRewardHandler)
        notificationsMgr.append(WindowNotificationCommand(window))
        return


@adisp.adisp_process
def showHalloweenShop():
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher is None:
        _logger.error('Prebattle dispatcher is not defined')
        return
    else:
        result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        if not result:
            _logger.error('Failed to switch prebattle entity')
            return
        showShop(getHalloween2023ShopUrl())
        return


@adisp.adisp_process
def showMissions(groupID):
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher is None:
        _logger.error('Prebattle dispatcher is not defined')
        return
    else:
        result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        if not result:
            _logger.error('Failed to switch prebattle entity')
            return
        showMissionsCategories(groupID=groupID)
        return


def showGlobalProgression():
    from halloween.gui.impl.lobby.global_progression_view import GlobalProgressionWindow
    layoutID = R.views.halloween.lobby.GlobalProgressionView()
    if isViewLoaded(layoutID):
        return
    wnd = GlobalProgressionWindow(layoutID)
    wnd.load()
