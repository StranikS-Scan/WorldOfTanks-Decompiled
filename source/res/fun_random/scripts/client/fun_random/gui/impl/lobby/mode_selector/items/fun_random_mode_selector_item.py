# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/mode_selector/items/fun_random_mode_selector_item.py
import typing
import math_utils
from fun_random.gui.feature.fun_constants import FunSubModesState
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression, hasAnySubMode, hasMultipleSubModes, avoidSubModesStates
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_progression_state import FunRandomProgressionStatus
from fun_random.gui.impl.lobby.common.fun_view_helpers import defineProgressionStatus
from fun_random.gui.impl.lobby.common.fun_view_helpers import getFormattedTimeLeft
from fun_random.gui.impl.lobby.mode_selector.items.fun_random_mode_selector_helpers import createSelectorHelper
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_fun_random_model import ModeSelectorFunRandomModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_fun_random_widget_model import SimpleFunProgressionStatus
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from helpers import time_utils
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from fun_random.gui.feature.models.common import FunSubModesStatus
    from fun_random.gui.impl.lobby.mode_selector.items.fun_random_mode_selector_helpers import IModeSelectorHelper
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_fun_random_widget_model import ModeSelectorFunRandomWidgetModel
_PROGRESSION_STATUS_MAP = {FunRandomProgressionStatus.ACTIVE_RESETTABLE: SimpleFunProgressionStatus.ACTIVE,
 FunRandomProgressionStatus.ACTIVE_FINAL: SimpleFunProgressionStatus.ACTIVE,
 FunRandomProgressionStatus.COMPLETED_RESETTABLE: SimpleFunProgressionStatus.RESETTABLE,
 FunRandomProgressionStatus.COMPLETED_FINAL: SimpleFunProgressionStatus.DISABLED,
 FunRandomProgressionStatus.DISABLED: SimpleFunProgressionStatus.DISABLED}

class FunRandomSelectorItem(ModeSelectorLegacyItem, FunAssetPacksMixin, FunSubModesWatcher, FunProgressionWatcher):
    __slots__ = ('__subModesHelper',)
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.FUN_RANDOM
    _VIEW_MODEL = ModeSelectorFunRandomModel

    def __init__(self, oldSelectorItem):
        super(FunRandomSelectorItem, self).__init__(oldSelectorItem)
        self.__subModesHelper = None
        return

    @property
    def viewModel(self):
        return self._viewModel

    @hasMultipleSubModes(defReturn=True)
    def checkHeaderNavigation(self):
        return False

    def setDisabledProgression(self):
        with self.viewModel.transaction() as model:
            model.widget.setStatus(SimpleFunProgressionStatus.DISABLED)
            self.__invalidateRewards(model.getRewardList())

    def handleInfoPageClick(self):
        self.showSubModesInfoPage()

    @hasMultipleSubModes(defReturn=True)
    def _isInfoIconVisible(self):
        return bool(self._funRandomCtrl.getSettings().infoPageUrl)

    def _isNewLabelVisible(self):
        isEntryPointAvailable = self._funRandomCtrl.subModesInfo.isEntryPointAvailable()
        return super(FunRandomSelectorItem, self)._isNewLabelVisible() and isEntryPointAvailable

    def _getModeStringsRoot(self):
        return self.getModeLocalsResRoot().mode_selector

    def _onInitializing(self):
        super(FunRandomSelectorItem, self)._onInitializing()
        self.__reloadModeHelper()
        self.__addListeners()
        self.__invalidateAll()

    def _onDisposing(self):
        self.__removeListeners()
        self.__subModesHelper.clear()
        super(FunRandomSelectorItem, self)._onDisposing()

    def __getStatusText(self, status):
        return backport.text(R.strings.fun_random.modeSelector.notStarted()) if not self._bootcamp.isInBootcamp() and status.state in FunSubModesState.BEFORE_STATES else ''

    def __getTimeLeftText(self, status):
        return getFormattedTimeLeft(time_utils.getTimeDeltaFromNowInLocal(status.rightBorder)) if status.state in FunSubModesState.INNER_STATES else ''

    def __addListeners(self):
        self.startSubSettingsListening(self.__invalidateAll)
        self.startSubStatusListening(self.__invalidateAll, tickMethod=self.__invalidateSubModesTimer)
        self.startProgressionListening(self.__invalidateProgression, tickMethod=self.__invalidateProgressionTimer)
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__invalidateNewLabel,
         'stats.unlocks': self.__invalidateNewLabel})

    def __removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.stopProgressionListening(self.__invalidateProgression, tickMethod=self.__invalidateProgressionTimer)
        self.stopSubStatusListening(self.__invalidateAll, tickMethod=self.__invalidateSubModesTimer)
        self.stopSubSettingsListening(self.__invalidateAll)

    @avoidSubModesStates(states=FunSubModesState.HIDDEN_SELECTOR_STATES, abortAction='onCardChange')
    def __invalidateAll(self, status=None, *_):
        self.__reloadModeHelper()
        with self.viewModel.transaction() as model:
            self.__fillCardModel(model, status)
            if status.state in FunSubModesState.INNER_STATES:
                self.__fillProgression(model.widget)
            else:
                self.setDisabledProgression()

    @hasActiveProgression(abortAction='setDisabledProgression')
    def __invalidateProgression(self, *_):
        with self.viewModel.transaction() as model:
            self.__invalidateRewards(model.getRewardList())
            self.__fillProgression(model.widget)

    @hasActiveProgression()
    def __invalidateProgressionTimer(self, *_):
        self.viewModel.widget.setResetTimer(self.getActiveProgression().condition.resetTimer)

    @hasAnySubMode()
    def __invalidateSubModesTimer(self, *_):
        self.viewModel.setTimeLeft(self.__getTimeLeftText(self.getSubModesStatus()))

    def __invalidateNewLabel(self, *_):
        self.viewModel.setIsNew(self._isNewLabelVisible())

    def __invalidateRewards(self, rewards):
        rewards.clear()
        self.__fillProgressionReward()
        rewards.invalidate()

    @hasAnySubMode(abortAction='onCardChange')
    def __fillCardModel(self, model, status):
        model.setResourcesFolderName(self.getModeAssetsPointer())
        model.setIsDisabled(self.__subModesHelper.isDisabled())
        model.setConditions(self.__subModesHelper.getConditionText())
        model.setStatusNotActive(self.__getStatusText(status))
        model.setTimeLeft(self.__getTimeLeftText(status))
        self.__invalidateRewards(model.getRewardList())

    @hasActiveProgression(abortAction='setDisabledProgression')
    def __fillProgression(self, model):
        progression = self.getActiveProgression()
        status = _PROGRESSION_STATUS_MAP.get(defineProgressionStatus(progression), SimpleFunProgressionStatus.DISABLED)
        condition, activeStage = progression.condition, progression.activeStage
        maximumPoints = activeStage.requiredCounter - activeStage.prevRequiredCounter
        currentPoints = condition.counter - activeStage.prevRequiredCounter
        model.setStatus(status)
        model.setCurrentStage(progression.state.currentStageIndex + 1)
        model.setConditionText(condition.text)
        model.setStageCurrentPoints(math_utils.clamp(0, maximumPoints, currentPoints))
        model.setStageMaximumPoints(maximumPoints)
        model.setResetTimer(condition.resetTimer)

    @hasActiveProgression()
    def __fillProgressionReward(self):
        self._addReward(ModeSelectorRewardID.OTHER, tooltipID=ModeSelectorTooltipsConstants.FUN_RANDOM_REWARDS)

    def __reloadModeHelper(self):
        if self.__subModesHelper is not None:
            self.__subModesHelper.clear()
        self.__subModesHelper = createSelectorHelper(self.getSubModes())
        return
