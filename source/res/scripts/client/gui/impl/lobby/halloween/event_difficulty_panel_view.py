# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/event_difficulty_panel_view.py
import WWISE
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.shared.utils import decorators
from gui.impl.gen.view_models.views.lobby.halloween.event_difficulty_item_model import EventDifficultyItemModel, StateEnum, AnimationTypeEnum
from gui.impl.gen.view_models.views.lobby.halloween.event_difficulty_panel_view_model import EventDifficultyPanelViewModel
from gui.impl.lobby.halloween.tooltips.event_difficulty_tooltip import EventDifficultyTooltip
from gui.impl.pub import ViewImpl
from gui.prb_control import prb_getters
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.event.squad.entity import EventBattleSquadEntity
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from gui.server_events.game_event.event_processors import ChangeSelectedDifficultyLevel
from gui.server_events.game_event.difficulty_progress import DifficultyLevelItem
from helpers.CallbackDelayer import CallbackDelayer
from constants import REQUEST_COOLDOWN
from gui.impl.lobby.halloween.sound_constants import EventHangarSound

class EventDifficultyPanelView(ViewImpl, IGlobalListener):
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, windowViewName=None):
        settings = ViewSettings(R.views.lobby.halloween.EventDifficultyPanelView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = EventDifficultyPanelViewModel()
        self.__windowViewName = windowViewName
        self.__selectedLevel = None
        self.__unlockedLevel = None
        self._callbackDelayer = CallbackDelayer()
        super(EventDifficultyPanelView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(EventDifficultyPanelView, self).getViewModel()

    def onUnitPlayerBecomeCreator(self, pInfo):
        if not pInfo.isCurrentPlayer():
            self.__updateModel(state=StateEnum.DISABLED)
        else:
            self.__updateModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.halloween.tooltips.EventDifficultyTooltip():
            level = event.getArgument('level')
            difficultyController = self.gameEventController.getDifficultyController()
            difficultyItem = next((item for item in difficultyController.getItems() if item.getDifficultyLevel() == level), None)
            return EventDifficultyTooltip(level, self.__selectedLevel == level, self.__unlockedLevel < level, difficultyItem.getCurrentProgress(), difficultyItem.getMaxProgress())
        else:
            return

    def _onLoading(self):
        super(EventDifficultyPanelView, self)._onLoading()
        self.startGlobalListening()
        self.viewModel.onClick += self.__onClick
        self.gameEventController.getDifficultyController().onItemsUpdated += self.__updateModel
        self.gameEventController.onSelectedDifficultyLevelChanged += self.__updateModel
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoinedOrLeft
            unitMgr.onUnitLeft += self.__onUnitJoinedOrLeft
        self.__updateModel()

    def _finalize(self):
        self.stopGlobalListening()
        self._callbackDelayer.destroy()
        self.viewModel.onClick -= self.__onClick
        self.gameEventController.onSelectedDifficultyLevelChanged -= self.__updateModel
        self.gameEventController.getDifficultyController().onItemsUpdated -= self.__updateModel
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__onUnitJoinedOrLeft
            unitMgr.onUnitLeft -= self.__onUnitJoinedOrLeft
        super(EventDifficultyPanelView, self)._finalize()

    def _showWaiting(self, show):
        if show:
            Waiting.show('sinhronize')
        else:
            Waiting.hide('sinhronize')

    def __onUnitJoinedOrLeft(self, _, __):
        if not bool(self.__windowViewName):
            self.__updateModel()

    def __updateModel(self, state=None):
        if state is None and isinstance(self.prbEntity, EventBattleSquadEntity) and not self.prbEntity.isCommander():
            state = StateEnum.DISABLED
        self.__selectedLevel = self.gameEventController.getSelectedDifficultyLevel()
        self.__unlockedLevel = self.gameEventController.getMaxUnlockedDifficultyLevel()
        with self.viewModel.transaction() as vm:
            vm.setIsDifficultyWindow(bool(self.__windowViewName))
            items = vm.getDifficulties()
            items.clear()
            for level in self.gameEventController.getDifficultyLevels():
                baseState = self.__getLevelState(level, self.__selectedLevel, self.__unlockedLevel)
                if self.__selectedLevel == level or state is None:
                    itemState = baseState
                else:
                    itemState = baseState if baseState == StateEnum.LOCKED else state
                needAnimate = self.__checkNeedAnimation(level, self.__selectedLevel, self.__unlockedLevel)
                difficultyItemModel = self.__fillDifficultyItem(level, itemState, needAnimate)
                items.addViewModel(difficultyItemModel)

            items.invalidate()
        return

    def __checkNeedAnimation(self, level, selectedLevel, unlockedLevel):
        if level == DifficultyLevelItem.EASY or level == selectedLevel:
            return False
        if level == unlockedLevel and self.__windowViewName:
            return True
        if self.gameEventController.getBattlesCountByDifficultyLevel(level) == 0 and self.gameEventController.hasDifficultyLevelToken(level):
            battlesCountOnPrevLevel = self.gameEventController.getBattlesCountByDifficultyLevel(level - 1)
            if battlesCountOnPrevLevel >= self.gameEventController.getBattlesCountToAnimateNextLevel():
                return True
        return False

    def __fillDifficultyItem(self, level, state, needAnimate):
        model = EventDifficultyItemModel()
        model.setLevel(level)
        model.setState(state)
        model.setAnimationType(self.__getAnimationType(needAnimate))
        return model

    def __onClick(self, args):
        level = int(args.get('level'))
        result = self.gameEventController.setSelectedDifficultyLevel(level)
        if result:
            WWISE.WW_eventGlobal(EventHangarSound.DIFFICULTY_LEVEL_EVENT.format(level))
            self.__selectDifficulty(level)
            items = self.viewModel.getDifficulties()
            for i in items:
                if i.getLevel() == level:
                    i.setState(StateEnum.SELECTED)

            items.invalidate()

    @decorators.process('sinhronize')
    def __selectDifficulty(self, level):
        if self.gameEventController.isEnabled() and isinstance(self.prbEntity, EventBattleSquadEntity) and self.prbEntity.isCommander():
            self._showWaiting(True)
            self._callbackDelayer.delayCallback(REQUEST_COOLDOWN.CMD_CHANGE_SELECTED_DIFFICULTY_LEVEL, lambda : self._showWaiting(False))
            yield ChangeSelectedDifficultyLevel(level).request()

    def __getLevelState(self, level, selected, unlocked):
        if level > unlocked:
            return StateEnum.LOCKED
        return StateEnum.SELECTED if level == selected else StateEnum.DEFAULT

    def __getAnimationType(self, needAnimate):
        if needAnimate:
            if self.__windowViewName:
                return AnimationTypeEnum.NEW
            return AnimationTypeEnum.HINT
        return AnimationTypeEnum.NO_ANIMATION
