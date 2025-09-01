# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/difficulty_view.py
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from account_helpers import AccountSettings
from helpers import dependency
from last_stand.gui.game_control.ls_difficulty_missions_controller import getFormattedMissionsList
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui.ls_gui_constants import DifficultyLevel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.difficulty_item_model import DifficultyItemModel, StateEnum
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.difficulty_view_model import DifficultyViewModel
from last_stand.gui.impl.lobby.tooltips.difficulty_tooltip import DifficultyTooltipView
from last_stand.gui.prb_control.entities.squad.entity import LastStandSquadEntity
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController

class DifficultyView(ViewComponent[DifficultyViewModel], IGlobalListener):
    _difficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    lsMissionsCtrl = dependency.descriptor(ILSDifficultyMissionsController)

    def __init__(self):
        super(DifficultyView, self).__init__(R.aliases.last_stand.shared.Difficulty(), DifficultyViewModel)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.difficulty_tooltip():
            difficulty = int(event.getArgument('level'))
            state = StateEnum(event.getArgument('state'))
            isLocked = event.getArgument('isLocked')
            return DifficultyTooltipView(isHangar=True, difficulty=difficulty, completedMissions=self.lsMissionsCtrl.getCompletedMissionsIndexByDifficulty(difficulty), state=state, isLocked=isLocked)
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
        self.lsMissionsCtrl.onDifficultyMissionsStatusUpdated += self.__updateMissionsStatus
        self.startGlobalListening()

    def _unsubscribe(self):
        self.viewModel.onSwichLevel -= self.__onSwitchLevel
        self._difficultyCtrl.onChangeDifficultyLevel -= self.__selectLevel
        self._difficultyCtrl.onChangeDifficultyLevelStatus -= self.__updateLevelStatus
        self.lsMissionsCtrl.onDifficultyMissionsStatusUpdated -= self.__updateMissionsStatus
        self.stopGlobalListening()
        super(DifficultyView, self)._unsubscribe()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        self.__onUpdateDifficultyLevelsViewState()

    def onUnitPlayerAdded(self, pInfo):
        self.__onUpdateDifficultyLevelsViewState()

    def onUnitPlayerRemoved(self, pInfo):
        self.__onUpdateDifficultyLevelsViewState()

    def __fillViewModel(self):
        selectedLevel = self._difficultyCtrl.getSelectedLevel()
        mCtrl = self.lsMissionsCtrl
        with self.viewModel.transaction() as model:
            difficulties = model.getDifficulties()
            difficulties.clear()
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
                levelModel.setMissionCount(mCtrl.getMissionsCount(level.level.value))
                levelModel.setCompletedMissions(getFormattedMissionsList(mCtrl.getCompletedMissionsIndexByDifficulty(level.level.value)))
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
        with self.viewModel.transaction() as model:
            isDisabled = isinstance(self.prbEntity, LastStandSquadEntity) and not self.prbEntity.isCommander()
            model.setIsDisabled(isDisabled)

    def __onSwitchLevel(self, result):
        selectedID = int(result.get('level', 1))
        self.__select(selectedID)

    def __select(self, level):
        self._difficultyCtrl.selectLevel(DifficultyLevel(level))

    def __updateMissionsStatus(self):
        self.__fillViewModel()
