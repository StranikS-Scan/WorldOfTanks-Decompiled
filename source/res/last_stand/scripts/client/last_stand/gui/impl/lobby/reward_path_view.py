# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/reward_path_view.py
import typing
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_artefact_view_model import RewardPathArtefactViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_difficulty_view_model import RewardPathDifficultyViewModel
from last_stand.gui.impl.lobby.base_view import SwitcherPresenter
from last_stand.gui.impl.lobby.gsw_cards.key_card_presenter import KeyCardPresenter
from last_stand.gui.impl.lobby.gsw_cards.quests_card_presenter import QuestsCardPresenter
from last_stand.gui.impl.lobby.ls_helpers import getArtefactState, fillRewards
from last_stand.gui.impl.lobby.tooltips.difficulty_tooltip import DifficultyTooltipView
from last_stand.gui.impl.lobby.tooltips.event_mission_tooltip import EventMissionsTooltip
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import REWARD_PATH_EXIT, REWARD_PATH_ENTER
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from ids_generators import SequenceIDGenerator
from frameworks.wulf import ViewEvent, View, WindowFlags
from gui.impl.gen import R
from gui.shared import g_eventBus, events
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_view_model import RewardPathViewModel
from last_stand.gui.shared.event_dispatcher import showMetaIntroView, showIntroVideo, showHangar
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from helpers import dependency
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_artefacts_controller import Artefact
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class RewardPathView(ViewComponent[RewardPathViewModel]):
    lsCtrl = dependency.descriptor(ILSController)
    lsArtefactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsDifficultyMissionsCtrl = dependency.descriptor(ILSDifficultyMissionsController)
    difficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    _MAX_BONUSES_IN_VIEW = 4

    def __init__(self, *args, **kwargs):
        super(RewardPathView, self).__init__(R.views.last_stand.mono.lobby.reward_path_view(), RewardPathViewModel, *args, **kwargs)
        self.__bonusCache = {}
        self.__idGen = SequenceIDGenerator()

    @property
    def viewModel(self):
        return super(RewardPathView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(RewardPathView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.mission_tooltip():
            artefactID = event.getArgument('artefactID', '')
            return EventMissionsTooltip(selectedArtefactID=artefactID, isHangar=False)
        if contentID == R.views.last_stand.mono.lobby.tooltips.difficulty_tooltip():
            difficulty = event.getArgument('difficulty', '')
            isLocked = event.getArgument('isLocked', '')
            completedMissions = self.lsDifficultyMissionsCtrl.getCompletedMissionsIndexByDifficulty(difficulty)
            return DifficultyTooltipView(False, difficulty, completedMissions, isLocked=isLocked)
        return super(RewardPathView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return [(self.viewModel.onViewLoaded, self.__onViewLoaded),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onShowIntro, self.__onShowIntro),
         (self.viewModel.onAbout, self.__onAbout),
         (self.viewModel.goToMission, self.__goToMission),
         (self.lsDifficultyMissionsCtrl.onDifficultyMissionsStatusUpdated, self.__updateMissionsStatus)]

    def _onLoading(self, *args, **kwargs):
        super(RewardPathView, self)._onLoading()
        self.__fillItems()

    def _initChildren(self):
        self._registerChild(R.aliases.last_stand.shared.Keys(), KeyCardPresenter())
        self._registerChild(R.aliases.last_stand.shared.Quests(), QuestsCardPresenter(isBadgeWidget=True))
        self._registerChild(R.aliases.last_stand.shared.Switcher(), SwitcherPresenter())

    def _initialize(self):
        super(RewardPathView, self)._initialize()
        playSound(REWARD_PATH_ENTER)
        showMetaIntroView(forceOpen=False, parent=self.getParentWindow())

    def _finalize(self):
        playSound(REWARD_PATH_EXIT)
        super(RewardPathView, self)._finalize()

    def __onShowIntro(self):
        showIntroVideo()

    def __onAbout(self):
        showMetaIntroView()

    def __goToMission(self, args):
        artefactID = args.get('artefactID', None)
        if artefactID is not None:
            self.lsArtefactsCtrl.selectedArtefactID = artefactID
            showHangar()
        return

    def __fillItems(self):
        with self.viewModel.transaction() as tx:
            self.__fillArtefacts(tx)
            self.__fillDifficultyMissions(tx)

    def __fillArtefacts(self, tx):
        artefacts = tx.getArtefacts()
        artefacts.clear()
        if self.lsArtefactsCtrl.selectedArtefactID is not None:
            tx.setSelectedArtefactID(self.lsArtefactsCtrl.selectedArtefactID)
        currentProgress = self.lsArtefactsCtrl.getCurrentArtefactProgress()
        maxProgress = self.lsArtefactsCtrl.getMaxArtefactsProgress()
        tx.setIsCompleted(currentProgress >= maxProgress)
        tx.setProgress(maxProgress - currentProgress)
        self.__bonusCache = {}
        for artefact in self.lsArtefactsCtrl.artefactsSorted():
            artefactVM = RewardPathArtefactViewModel()
            artefactVM.setId(artefact.artefactID)
            artefactVM.setIndex(self.lsArtefactsCtrl.getIndex(artefact.artefactID))
            artefactVM.setState(getArtefactState(artefact.artefactID))
            artefactVM.getTypes().clear()
            for type in artefact.artefactTypes:
                artefactVM.getTypes().addString(type)

            artefactVM.getRewards().clear()
            self.__bonusCache.update(fillRewards(artefact.bonusRewards, artefactVM.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen, skipBonuses=['slots']))
            artefacts.addViewModel(artefactVM)

        artefacts.invalidate()
        return

    def __fillDifficultyMissions(self, tx):
        difficulties = tx.getDifficulties()
        difficulties.clear()
        selectedLevel = self.difficultyCtrl.getSelectedLevel()
        for level in self.difficultyCtrl.getLevelsInfo():
            difficultyVM = RewardPathDifficultyViewModel()
            difficultyVM.setLevel(level.level.value)
            difficultyVM.setIsLocked(not level.isUnlock)
            difficultyVM.setIsSelected(level.level == selectedLevel)
            sortedMissions = self.lsDifficultyMissionsCtrl.missionsSorted(level.level.value)
            difficultyVM.setIsCompleted(all((m.isCompleted for m in sortedMissions)))
            difficultyVM.getAggregatedRewards().clear()
            self.__bonusCache.update(fillRewards(self.lsDifficultyMissionsCtrl.getAggregatedMissionRewards(level.level.value), difficultyVM.getAggregatedRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen, skipBonuses=['slots']))
            difficulties.addViewModel(difficultyVM)

        difficulties.invalidate()

    def __onClose(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def __updateMissionsStatus(self):
        with self.viewModel.transaction() as tx:
            self.__fillDifficultyMissions(tx)


class RewardPathWindow(WindowImpl):

    def __init__(self, layer, *args, **kwargs):
        super(RewardPathWindow, self).__init__(content=RewardPathView(*args, **kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
