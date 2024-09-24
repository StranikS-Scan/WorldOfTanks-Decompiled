# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/main_view.py
from collections import deque
from typing import TYPE_CHECKING
from account_helpers.AccountSettings import LOOT_BOXES_INTRO_VIDEO_SHOWN
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.main_view_model import MainViewModel, SubViewID
from gui.impl.lobby.lootbox_system.common import MainViewImpl, PresentersMap
from gui.impl.pub.lobby_window import LobbyWindow
from gui.lootbox_system.common import ViewID, Views
from gui.lootbox_system.sound import enterLootBoxesSoundState, exitLootBoxesSoundState
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController
if TYPE_CHECKING:
    from typing import Any, Dict, Deque, Optional, Tuple

class _Presenters(PresentersMap):

    def _makeLoadersMap(self):
        return {SubViewID.NO_BOXES: self.__loadNoBoxes,
         SubViewID.HAS_BOXES: self.__loadHasBoxes,
         SubViewID.SINGLE_BOX_REWARDS: self.__loadSingleBoxRewards,
         SubViewID.MULTIPLE_BOXES_REWARDS: self.__loadMultipleBoxesRewards}

    def __loadNoBoxes(self):
        from gui.impl.lobby.lootbox_system.submodels.no_boxes import NoBoxes
        return NoBoxes(self._mainView.viewModel.noBoxes, self._mainView)

    def __loadHasBoxes(self):
        from gui.impl.lobby.lootbox_system.submodels.has_boxes import HasBoxes
        return HasBoxes(self._mainView.viewModel.hasBoxes, self._mainView)

    def __loadSingleBoxRewards(self):
        from gui.impl.lobby.lootbox_system.submodels.single_box_rewards import SingleBoxRewards
        return SingleBoxRewards(self._mainView.viewModel.singleBoxRewards, self._mainView)

    def __loadMultipleBoxesRewards(self):
        from gui.impl.lobby.lootbox_system.submodels.multiple_boxes_rewards import MultipleBoxesRewards
        return MultipleBoxesRewards(self._mainView.viewModel.multipleBoxesRewards, self._mainView)


class MainView(MainViewImpl):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, subViewID=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.lootbox_system.MainView())
        settings.model = MainViewModel()
        settings.args = (subViewID,) + args
        settings.kwargs = kwargs
        super(MainView, self).__init__(settings)
        self.__subviews = None
        self.__subviewID = None
        self.__pendingSubviews = deque()
        return

    @property
    def viewModel(self):
        return super(MainView, self).getViewModel()

    @property
    def currentSubview(self):
        return self.__subviews[self.__subviewID]

    def createToolTip(self, event):
        return self.currentSubview.createToolTip(event) or super(MainView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return self.currentSubview.createToolTipContent(event, contentID) or super(MainView, self).createToolTipContent(event, contentID)

    def switchToSubView(self, subViewID=None, isBackground=False, *args, **kwargs):
        self.__addSubview(subViewID, *args, **kwargs)
        if not isBackground:
            self.__loadPendingSubviews()

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loading')
        self.__subviews = self._getPresentersMap()
        super(MainView, self)._onLoading(*args, **kwargs)
        self.switchToSubView(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        self.__showIntroIfNeeded()
        enterLootBoxesSoundState()

    def _finalize(self):
        exitLootBoxesSoundState()
        self.__pendingSubviews = deque()
        self.__subviews.clear()
        super(MainView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onResourcesLoadCompleted, self.__onResourcesLoadCompleted), (self.__lootBoxes.onStatusChanged, self.__onStatusChanged), (self.__lootBoxes.onBoxesAvailabilityChanged, self.__onStatusChanged))

    def _getPresentersMap(self):
        return _Presenters(self)

    def _getDefaultSubViewID(self):
        return SubViewID.HAS_BOXES if self.__lootBoxes.getBoxesCount() else SubViewID.NO_BOXES

    def __onResourcesLoadCompleted(self):
        Waiting.hide('loading')

    def __addSubview(self, subViewID=None, *args, **kwargs):
        subViewID = SubViewID(subViewID) if subViewID is not None else self._getDefaultSubViewID()
        self.__pendingSubviews.append((subViewID, args, kwargs))
        return

    def __loadPendingSubviews(self):
        with self.viewModel.transaction() as vmTx:
            subviewIDsModel = vmTx.getSubViewIDs()
            subviewIDsModel.clear()
            while self.__pendingSubviews:
                subviewID, args, kwargs = self.__pendingSubviews.popleft()
                if self.currentSubview is not None:
                    self.currentSubview.finalize()
                self.__subviewID = subviewID
                self.currentSubview.initialize(*args, **kwargs)
                subviewIDsModel.addNumber(self.__subviewID)

            subviewIDsModel.invalidate()
        return

    def __showIntroIfNeeded(self):
        if not self.__lootBoxes.getSetting(LOOT_BOXES_INTRO_VIDEO_SHOWN):
            Views.load(ViewID.INTRO)
            self.__lootBoxes.setSetting(LOOT_BOXES_INTRO_VIDEO_SHOWN, True)

    def __onStatusChanged(self):
        if not (self.__lootBoxes.isActive and self.__lootBoxes.isLootBoxesAvailable):
            self.destroy()


class MainWindow(LobbyWindow):

    def __init__(self, subViewID=None, *args, **kwargs):
        super(MainWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=MainView(subViewID, *args, **kwargs))
