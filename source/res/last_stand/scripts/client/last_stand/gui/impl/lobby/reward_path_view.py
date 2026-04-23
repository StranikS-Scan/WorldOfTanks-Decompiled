# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/reward_path_view.py
from __future__ import absolute_import
import typing
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_artefact_view_model import RewardPathArtefactViewModel
from last_stand.gui.impl.lobby.base_view import SwitcherPresenter
from last_stand.gui.impl.lobby.gsw_cards.quests_card_presenter import QuestsCardPresenter
from last_stand.gui.impl.lobby.ls_helpers import fillRewards
from last_stand.gui.impl.lobby.tooltips.additional_data_tooltip import AdditionalDataTooltipView
from last_stand.gui.impl.lobby.tooltips.booster_tooltip import BoosterTooltipView
from last_stand.gui.impl.lobby.tooltips.points_tooltip import PointsTooltipView
from last_stand.gui.impl.lobby.widgets.bundle_card import BundleCard
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import REWARD_PATH_EXIT, REWARD_PATH_ENTER
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from ids_generators import SequenceIDGenerator
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.shared import g_eventBus, events
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_view_model import RewardPathViewModel
from last_stand.gui.shared.event_dispatcher import showMetaIntroView
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from helpers import dependency
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_artefacts_controller import Artefact
    from frameworks.wulf import ViewEvent, View
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class RewardPathView(ViewComponent[RewardPathViewModel]):
    lsCtrl = dependency.descriptor(ILSController)
    lsArtefactsCtrl = dependency.descriptor(ILSArtefactsController)
    difficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    _MAX_BONUSES_IN_VIEW = 6

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
        if contentID == R.views.last_stand.mono.lobby.tooltips.booster_tooltip():
            boosterName = event.getArgument('boosterName', '')
            return BoosterTooltipView(boosterName)
        if contentID == R.views.last_stand.mono.lobby.tooltips.additional_data_tooltip():
            return AdditionalDataTooltipView()
        return PointsTooltipView(isPostBattle=False) if contentID == R.views.last_stand.mono.lobby.tooltips.points_tooltip() else super(RewardPathView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return [(self.viewModel.onViewLoaded, self.__onViewLoaded),
         (self.viewModel.onClose, self.__onClose),
         (self.lsArtefactsCtrl.onProgressPointsUpdated, self.__onPointsUpdated),
         (self.lsArtefactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated)]

    def _onLoading(self, *args, **kwargs):
        super(RewardPathView, self)._onLoading(*args, **kwargs)
        self.__fillItems()

    def _getChildComponents(self):
        lsAliases = R.aliases.last_stand.shared
        return {lsAliases.Switcher(): SwitcherPresenter,
         lsAliases.Quests(): QuestsCardPresenter,
         lsAliases.BundleCard(): BundleCard}

    def _initialize(self, *args, **kwargs):
        super(RewardPathView, self)._initialize(*args, **kwargs)
        playSound(REWARD_PATH_ENTER)
        if self.lsCtrl.isMetaInfoEnabled():
            showMetaIntroView(forceOpen=False, parent=self.getParentWindow())

    def _finalize(self):
        playSound(REWARD_PATH_EXIT)
        super(RewardPathView, self)._finalize()

    def __fillItems(self):
        with self.viewModel.transaction() as tx:
            self.__fillArtefacts(tx)

    def __fillArtefacts(self, tx):
        currentProgressByArtefactId = ''
        artefacts = tx.getArtefacts()
        artefacts.clear()
        self.__bonusCache = {}
        for artefact in self.lsArtefactsCtrl.artefactsSorted():
            isOpened = self.lsArtefactsCtrl.isArtefactOpened(artefact.artefactID)
            artefactVM = RewardPathArtefactViewModel()
            artefactVM.setId(artefact.artefactID)
            artefactVM.setIndex(self.lsArtefactsCtrl.getIndex(artefact.artefactID))
            artefactVM.setIsCompleted(isOpened)
            artefactVM.setCost(self.lsArtefactsCtrl.getArtefactProgressPointsCost(artefact.artefactID))
            if not isOpened and not currentProgressByArtefactId:
                currentProgressByArtefactId = artefact.artefactID
            artefactVM.getRewards().clear()
            self.__bonusCache.update(fillRewards(artefact.bonusRewards, artefactVM.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen))
            artefacts.addViewModel(artefactVM)

        tx.setCurrentArtefactID(currentProgressByArtefactId)
        tx.setPoints(self.lsArtefactsCtrl.getProgressPointsQuantity())
        artefacts.invalidate()

    def __onClose(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def __onPointsUpdated(self):
        self.viewModel.setPoints(self.lsArtefactsCtrl.getProgressPointsQuantity())

    def __onArtefactStatusUpdated(self, *args):
        self.__fillItems()


class RewardPathWindow(WindowImpl):

    def __init__(self, layer, *args, **kwargs):
        super(RewardPathWindow, self).__init__(content=RewardPathView(*args, **kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
