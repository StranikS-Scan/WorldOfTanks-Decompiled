# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/paragons_entry_point_view.py
import weakref
from gui.impl.gen.view_models.views.lobby.paragons.paragons_entry_point_view_model import ParagonsEntryPointViewModel, ProgressState
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel
from gui.impl.lobby.paragons.paragons_window_events import showParagonsNavigationView
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillChapterModel
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from helpers import dependency
from paragons_common import ParagonsEntitlements, getParagonsEntitlement
from skeletons.gui.game_control import IParagonsController, IParagonsRewardsShopController
from skeletons.gui.techtree_events import ITechTreeEventsListener

class ParagonsEntryPoint(object):
    __slots__ = ('__viewRef', '__paragonsStateToTabId')
    __paragonsController = dependency.descriptor(IParagonsController)
    __selectableRewardsController = dependency.descriptor(IParagonsRewardsShopController)
    __techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)

    def __init__(self, view):
        self.__viewRef = weakref.ref(view)
        self.__paragonsStateToTabId = {ProgressState.CHAPTERNOTCHOSEN: TabId.CHAPTERS,
         ProgressState.ALLCHAPTERSCOMPLETED: TabId.CHAPTERS,
         ProgressState.ACTIVE: TabId.PROGRESS,
         ProgressState.PAUSED: None,
         ProgressState.NOTAVAILABLE: TabId.CHAPTERS}
        return

    @property
    def viewModel(self):
        return self.__viewRef().viewModel.paragonsEntryPoint

    def init(self):
        self.viewModel.onEntryPointClick += self.__onClick
        self.__paragonsController.onSettingsChanged += self.__updateCloseoutTimer
        self.__paragonsController.onParagonsStateChanged += self.__updateCloseoutTimer
        self.__paragonsController.onFeatureStateChanged += self.__updateCloseoutTimer
        if self.__techTreeEventsListener.isParagonsEntryPointEnabled():
            self.update()
            self.__updateCloseoutTimer()

    def fini(self):
        self.viewModel.onEntryPointClick -= self.__onClick
        self.__paragonsController.onSettingsChanged -= self.__updateCloseoutTimer
        self.__paragonsController.onParagonsStateChanged -= self.__updateCloseoutTimer
        self.__paragonsController.onFeatureStateChanged -= self.__updateCloseoutTimer

    def update(self, isNeedUpdateLevels=True):
        if not self.__paragonsController.isEnabled:
            return
        else:
            paragonsState = self.__getParagonsState()
            chosenChapterID = self.__paragonsController.chapterID
            with self.viewModel.transaction() as tx:
                tx.setProgressState(paragonsState)
                tx.setIsAnySelectableReward(self.__isAnySelectableReward())
                tx.setIsAnySelectableRewardInInventory(self.__isAnySelectableRewardInInventory())
                tx.setFreePoints(self.__paragonsController.progress if chosenChapterID is None else 0)
                self.__fillChapterModel(tx.currentChapter, paragonsState, isNeedUpdateLevels)
            return

    def __updateCloseoutTimer(self, *args, **kwargs):
        self.viewModel.setCloseoutTimeStamp(self.__paragonsController.getClosestChapterCloseoutTimeStamp())

    def __getParagonsState(self):
        ctrl = self.__paragonsController
        chosenChapter = ctrl.chapterID
        isAllChaptersComplete = all((ctrl.isChapterComplete(chapterID) for chapterID in ctrl.availableChapterIDs))
        isPaused = ctrl.isPaused
        isAnyChapterAvailable = ctrl.isAnyChapterAvailable
        if isPaused:
            return ProgressState.PAUSED
        elif isAllChaptersComplete:
            return ProgressState.ALLCHAPTERSCOMPLETED
        elif chosenChapter is None and not ctrl.wasBranchResetEverAvailable:
            return ProgressState.NOTAVAILABLE
        else:
            return ProgressState.CHAPTERNOTCHOSEN if chosenChapter is None and isAnyChapterAvailable else ProgressState.ACTIVE

    def __isAnySelectableReward(self):
        chapterID = self.__paragonsController.chapterID
        entID = getParagonsEntitlement(ParagonsEntitlements.all()[chapterID - 1 if chapterID else 0])
        entitlements = self.__selectableRewardsController.entitlements
        return bool(entitlements.getEntitlementsByID(entID))

    def __isAnySelectableRewardInInventory(self):
        return any((vehicle.isInInventory for vehicle in self.__paragonsController.getMaxLevelVehicles()))

    def __fillChapterModel(self, chapterModel, paragonsState, isNeedUpdateLevels=True):
        if paragonsState != ProgressState.ACTIVE:
            return
        ctrl = self.__paragonsController
        isChapterModelEmpty = len(chapterModel.getLevels())
        isNeedUpdateLevels = isNeedUpdateLevels or not isChapterModelEmpty
        fillChapterModel(chapterModel, ctrl.chapterID, isNeedUpdateLevels=isNeedUpdateLevels)

    def __onClick(self):
        state = self.viewModel.getProgressState()
        tabId = self.__paragonsStateToTabId.get(state)
        if tabId is not None:
            showParagonsNavigationView(parent=self.__viewRef().getParentWindow(), tabId=tabId)
        return
