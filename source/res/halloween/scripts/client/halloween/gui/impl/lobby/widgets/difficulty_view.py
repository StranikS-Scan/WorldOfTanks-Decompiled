# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/widgets/difficulty_view.py
from __future__ import absolute_import
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewStatus
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from account_helpers import AccountSettings
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.gui.halloween_gui_constants import DifficultyLevel
from halloween.gui.impl.gen.view_models.views.lobby.widgets.difficulty_item_model import DifficultyItemModel, StateEnum
from halloween.gui.impl.gen.view_models.views.lobby.widgets.difficulty_view_model import DifficultyViewModel
from halloween.gui.impl.lobby.tooltips.difficulty_tooltip import DifficultyTooltipView
from halloween.gui.prb_control.entities.squad.entity import HalloweenSquadEntity
from halloween.skeletons.difficulty_level_controller import IDifficultyLevelController
from helpers import dependency

class DifficultyView(ViewComponent[DifficultyViewModel], IGlobalListener):
    _difficultyCtrl = dependency.descriptor(IDifficultyLevelController)

    def __init__(self):
        super(DifficultyView, self).__init__(R.aliases.halloween.shared.Difficulty(), DifficultyViewModel)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.difficulty_tooltip():
            level = int(event.getArgument('level'))
            state = StateEnum(event.getArgument('state'))
            isLocked = event.getArgument('isLocked')
            return DifficultyTooltipView(level=level, state=state, isLocked=isLocked)
        return super(DifficultyView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(DifficultyView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onPrbEntitySwitched(self):
        super(DifficultyView, self).onPrbEntitySwitched()
        self.__onUpdateDifficultyLevelsViewState()

    def _onLoading(self, *args, **kwargs):
        super(DifficultyView, self)._onLoading()
        self.__fillViewModel()
        self.__onUpdateDifficultyLevelsViewState()

    def _subscribe(self):
        super(DifficultyView, self)._subscribe()
        self.viewModel.onSwichLevel += self.__onSwitchLevel
        self._difficultyCtrl.onChangeDifficultyLevel += self.__selectLevel
        self._difficultyCtrl.onChangeDifficultyLevelStatus += self.__updateLevelStatus
        g_playerEvents.onEnqueued += self.__onUpdateDifficultyLevelsViewState
        g_playerEvents.onDequeued += self.__onUpdateDifficultyLevelsViewState
        g_playerEvents.onKickedFromArena += self.__onUpdateDifficultyLevelsViewState
        g_playerEvents.onEnqueueFailure += self.__onUpdateDifficultyLevelsViewState
        self.startGlobalListening()

    def _unsubscribe(self):
        self.viewModel.onSwichLevel -= self.__onSwitchLevel
        self._difficultyCtrl.onChangeDifficultyLevel -= self.__selectLevel
        self._difficultyCtrl.onChangeDifficultyLevelStatus -= self.__updateLevelStatus
        g_playerEvents.onEnqueued -= self.__onUpdateDifficultyLevelsViewState
        g_playerEvents.onDequeued -= self.__onUpdateDifficultyLevelsViewState
        g_playerEvents.onKickedFromArena -= self.__onUpdateDifficultyLevelsViewState
        g_playerEvents.onEnqueueFailure -= self.__onUpdateDifficultyLevelsViewState
        self.stopGlobalListening()
        super(DifficultyView, self)._unsubscribe()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        self.__onUpdateDifficultyLevelsViewState()

    def onUnitPlayerAdded(self, pInfo):
        self.__onUpdateDifficultyLevelsViewState()

    def onUnitPlayerRemoved(self, pInfo):
        self.__onUpdateDifficultyLevelsViewState()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.__onUpdateDifficultyLevelsViewState()

    def __fillViewModel(self):
        selectedLevel = self._difficultyCtrl.getSelectedLevel()
        with self.viewModel.transaction() as model:
            difficulties = model.getDifficulties()
            settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
            unlockedLevels = settings[AccountSettingsKeys.UNLOCK_LEVELS]
            for level in self._difficultyCtrl.getLevelsInfo():
                levelModel = DifficultyItemModel()
                levelModel.setLevel(level.level.value)
                if level.level == selectedLevel:
                    levelModel.setState(StateEnum.SELECTED)
                else:
                    levelModel.setState(StateEnum.DEFAULT)
                levelModel.setIsNew(unlockedLevels.get(level.level.value, {}).get('isNew', False))
                levelModel.setIsLocked(not level.isUnlock)
                difficulties.addViewModel(levelModel)

            difficulties.invalidate()

    def __selectLevel(self, level):
        with self.viewModel.transaction() as model:
            levels = model.getDifficulties()
            for item in levels:
                if level.value == item.getLevel():
                    item.setState(StateEnum.SELECTED)
                    item.setIsNew(False)
                item.setState(StateEnum.DEFAULT)

            levels.invalidate()

    def __updateLevelStatus(self, level):
        with self.viewModel.transaction() as model:
            settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
            unlockedLevels = settings[AccountSettingsKeys.UNLOCK_LEVELS]
            levels = model.getDifficulties()
            for item in levels:
                if level.level.value != item.getLevel():
                    continue
                item.setIsLocked(not level.isUnlock)
                item.setIsNew(unlockedLevels.get(level.level.value, {}).get('isNew', False))

            levels.invalidate()

    def __onUpdateDifficultyLevelsViewState(self, *args, **kwargs):
        if self.viewStatus in (ViewStatus.DESTROYED, ViewStatus.DESTROYING) or self.viewModel is None:
            return
        elif not self.prbEntity:
            return
        else:
            with self.viewModel.transaction() as model:
                if isinstance(self.prbEntity, HalloweenSquadEntity):
                    isDisabled = self.prbEntity.isInQueue() or not self.prbEntity.isCommander()
                else:
                    isDisabled = self.prbEntity.isInQueue()
                model.setIsDisabled(isDisabled)
            return

    def __onSwitchLevel(self, args):
        selectedID = int(args.get('level', 1))
        self._difficultyCtrl.selectLevel(DifficultyLevel(selectedID))
