# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/entry_point_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.entry_point_tooltip_model import EntryPointTooltipModel, ProgressState
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import fillChapterModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IParagonsController

class EntryPointTooltip(ViewImpl):
    __slots__ = ()
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.paragons.tooltips.EntryPointTooltip())
        settings.model = EntryPointTooltipModel()
        super(EntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPointTooltip, self)._onLoading()
        currentState = self.__getParagonsState()
        with self.viewModel.transaction() as tx:
            tx.setProgressState(currentState)
            tx.setPoints(self.__paragonsController.progress)
            tx.setVehicleToReset(self.__paragonsController.minUnlockedNecessaryLevelVehiclesCount)
            tx.setIsFirstEntry(self.__isFirstEntry(currentState))
            self.__fillChapterModel(tx.currentChapter, currentState)

    def __getParagonsState(self):
        ctrl = self.__paragonsController
        chosenChapter = ctrl.chapterID
        isAllChaptersComplete = all((ctrl.isChapterComplete(chapterID) for chapterID in ctrl.availableChapterIDs))
        isPaused = ctrl.isPaused
        isAnyChapterAvailable = ctrl.isAnyChapterAvailable
        isNotEnoughNecessaryVehicles = ctrl.unlockedNecessaryLevelVehiclesCount < ctrl.minUnlockedNecessaryLevelVehiclesCount
        if isPaused:
            return ProgressState.PAUSED
        elif chosenChapter is None and isAnyChapterAvailable:
            return ProgressState.CHAPTERNOTCHOSEN
        elif isAllChaptersComplete:
            return ProgressState.ALLCHAPTERSCOMPLETED
        elif not ctrl.branches.resetBranchesCount:
            return ProgressState.NORESETTEDBRANCHES
        else:
            return ProgressState.NEEDVEHICLETORESET if isNotEnoughNecessaryVehicles else ProgressState.ACTIVE

    def __isFirstEntry(self, currentState):
        return currentState == ProgressState.CHAPTERNOTCHOSEN and not any((self.__paragonsController.isChapterComplete(chapterID) for chapterID in self.__paragonsController.availableChapterIDs))

    def __fillChapterModel(self, chapterModel, currentState):
        if currentState not in (ProgressState.CHAPTERNOTCHOSEN, ProgressState.PAUSED, ProgressState.ALLCHAPTERSCOMPLETED):
            fillChapterModel(chapterModel, self.__paragonsController.chapterID)
