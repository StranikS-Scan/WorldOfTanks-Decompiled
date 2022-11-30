# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_reward_base_view.py
import BigWorld
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_reward_view_model import ChallengeRewardViewModel
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, nyCreateToolTipContentDecorator
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.events import NyGladeVisibilityEvent, LobbySimpleEvent
from helpers import dependency
from new_year.ny_preview import getVehiclePreviewID
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class ChallengeRewardBaseView(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.instance(IAppLoader)

    def __init__(self, settings, *args, **kwargs):
        super(ChallengeRewardBaseView, self).__init__(settings, *args, **kwargs)
        self.__isInPreview = False

    @property
    def viewModel(self):
        return super(ChallengeRewardBaseView, self).getViewModel()

    @property
    def isInPreview(self):
        return self.__isInPreview

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        return super(ChallengeRewardBaseView, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChallengeRewardBaseView, self).createToolTip(event)

    def _onLoaded(self, *args, **kwargs):
        setOverlayHangarGeneral(onState=True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_SCREEN_REWARD)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': False}), scope=EVENT_BUS_SCOPE.LOBBY)
        super(ChallengeRewardBaseView, self)._onLoaded(*args, **kwargs)

    def _onLoading(self, *args, **kwargs):
        super(ChallengeRewardBaseView, self)._onLoading()
        with self.viewModel.transaction() as model:
            self._fillModel(model)

    def _fillModel(self, model):
        model.setRecommendedGraphicsPreset(BigWorld.detectGraphicsPresetFromSystemSettings())

    def _getEvents(self):
        events = super(ChallengeRewardBaseView, self)._getEvents()
        return events + ((self.viewModel.onStylePreview, self._onShowStylePreview), (self._nyController.onStateChanged, self.__onEventStateChanged))

    def _initialize(self, *args, **kwargs):
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_IN), scope=EVENT_BUS_SCOPE.DEFAULT)

    def _finalize(self):
        setOverlayHangarGeneral(onState=False)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.MESSENGER_BAR_VISIBLE, ctx={'visible': True}), scope=EVENT_BUS_SCOPE.LOBBY)
        super(ChallengeRewardBaseView, self)._finalize()

    def __onEventStateChanged(self):
        if not self._nyController.isEnabled():
            self.destroyWindow()

    def _backCallback(self):
        pass

    def _showBackBtn(self):
        return None

    def _showCloseBtn(self):
        return None

    def _onShowStylePreview(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self.__itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None:
            return
        else:
            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=self._backCallback, showBackBtn=self._showBackBtn(), showCloseBtn=self._showCloseBtn())
            NewYearNavigation.onAnchorSelected('')
            self.__isInPreview = True
            self.destroyWindow()
            return

    def _changeLayersVisibility(self, isHide, layers):
        lobby = self.__appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(layers, time=0.3)
            else:
                lobby.containerManager.showContainers(layers, time=0.3)
            self.__appLoader.getApp().graphicsOptimizationManager.switchOptimizationEnabled(not isHide)
