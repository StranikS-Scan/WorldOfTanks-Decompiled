# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_progression_view.py
import logging
import typing
from account_helpers.AccountSettings import AccountSettings, EVENT_LAST_STAMPS_SEEN, EVENT_LAST_LEVEL_SEEN
from frameworks.wulf import ViewFlags, ViewSettings, ViewEvent
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_progression_level_model import WtProgressionLevelModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_progression_view_model import WtProgressionViewModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.lobby.wt_event.tooltips.wt_event_stamp_tooltip_view import WtEventStampTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.wt_event.wt_event_helpers import backportTooltipDecorator, getInfoPageURL
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.entities.View import ViewKey
_logger = logging.getLogger(__name__)

class WTEventProgressionView(ViewImpl):
    __slots__ = ('_tooltipItems', '__isGrowingAnimation', '__fromWelcome')
    __gameEventController = dependency.descriptor(IEventBattlesController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventProgression(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=WtProgressionViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventProgressionView, self).__init__(settings)
        self._tooltipItems = None
        self.__isGrowingAnimation = False
        self.__fromWelcome = kwargs.get('fromWelcome', False)
        return

    @property
    def viewModel(self):
        return super(WTEventProgressionView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTEventProgressionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventTicketTooltipView():
            return WtEventTicketTooltipView()
        return WtEventStampTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtEventStampTooltipView() else super(WTEventProgressionView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        if self.__fromWelcome:
            Waiting.show('loadContent')
        super(WTEventProgressionView, self)._onLoading()
        self.__updateViewModel()
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        super(WTEventProgressionView, self)._onLoaded(*args, **kwargs)
        if self.__fromWelcome:
            Waiting.hide('loadContent')
        wt_event_sound.playProgressionViewEnter()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__removeListeners()
        self._tooltipItems = None
        wt_event_sound.playProgressionViewExit()
        if self.__isGrowingAnimation:
            wt_event_sound.playProgressBarGrowing(False)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        super(WTEventProgressionView, self)._finalize()
        return

    def __updateViewModel(self):
        self._tooltipItems = {}
        with self.viewModel.transaction() as model:
            self.__fillProgression(model)

    def __fillProgression(self, model):
        model.progression.clearItems()
        previousLevel = AccountSettings.getSettings(EVENT_LAST_LEVEL_SEEN)
        previousStamps = AccountSettings.getSettings(EVENT_LAST_STAMPS_SEEN)
        currentStamps = self.__gameEventController.getCurrentStampsCount()
        stampsPerLevel = self.__gameEventController.getStampsCountPerLevel()
        totalLevels = self.__gameEventController.getTotalLevelsCount()
        currentLevel = self.__gameEventController.getCurrentLevel()
        finishedLevel = self.__gameEventController.getFinishedLevelsCount()
        isCompleted = finishedLevel == totalLevels
        hasMadeProgress = previousLevel < currentLevel
        model.setPreviousLevel(previousLevel)
        model.setCurrentLevel(currentLevel)
        model.setTotalPoints(stampsPerLevel)
        model.setTotalLevel(totalLevels)
        model.setPreviousAllPoints(previousStamps)
        model.setCurrentAllPoints(currentStamps)
        model.setShowLevelsAnimations(hasMadeProgress)
        model.setIsCompleted(isCompleted)
        if hasMadeProgress:
            wt_event_sound.playProgressionLevelChanged()
        AccountSettings.setSettings(EVENT_LAST_LEVEL_SEEN, currentLevel)
        AccountSettings.setSettings(EVENT_LAST_STAMPS_SEEN, currentStamps)
        progression = self.__getItemsProgression()
        for level, rewards in progression:
            item = WtProgressionLevelModel()
            item.setLevel(level)
            packBonusModelAndTooltipData(rewards, item.rewardItems, self._tooltipItems, getWtEventBonusPacker())
            model.progression.addViewModel(item)

    def __getItemsProgression(self):
        result = []
        for data in self.__gameEventController.getConfig().progression:
            rewards = self.__gameEventController.getQuestRewards(data.get('quest', ''))
            result.append((data.get('level', 0), rewards))

        return result

    @staticmethod
    def __onAboutClick():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BROWSER_OVERLAY)

    def __addListeners(self):
        self.viewModel.onAboutClick += self.__onAboutClick
        self.__gameEventController.onEventPrbChanged += self.__onEventPrbChanged
        self.__gameEventController.onProgressUpdated += self.__updateViewModel

    def __removeListeners(self):
        self.viewModel.onAboutClick -= self.__onAboutClick
        self.__gameEventController.onEventPrbChanged -= self.__onEventPrbChanged
        self.__gameEventController.onProgressUpdated -= self.__updateViewModel

    def __onEventPrbChanged(self, isActive):
        self.__checkAndCloseBrowserView()
        if not isActive:
            self.destroyWindow()

    def __checkAndCloseBrowserView(self):
        app = self.__appLoader.getApp()
        if app is None:
            return
        else:
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.BROWSER_OVERLAY))
            if view is None:
                return
            view.destroy()
            return
