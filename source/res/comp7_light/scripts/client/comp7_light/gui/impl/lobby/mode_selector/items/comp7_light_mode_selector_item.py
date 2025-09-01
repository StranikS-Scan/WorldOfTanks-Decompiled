# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/mode_selector/items/comp7_light_mode_selector_item.py
from comp7_light.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_light_model import ModeSelectorComp7LightModel
from comp7_light.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_light_widget_model import Comp7LightProgressionStatus
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.shared.formatters import time_formatters
from helpers import dependency, time_utils, int2roman
from skeletons.gui.game_control import IComp7LightController

class Comp7LightModeSelectorItem(ModeSelectorLegacyItem):
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __comp7LightProgressionController = dependency.descriptor(IComp7LightProgressionController)
    _VIEW_MODEL = ModeSelectorComp7LightModel

    @property
    def viewModel(self):
        return super(Comp7LightModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(Comp7LightModeSelectorItem, self)._onInitializing()
        self.__updateComp7LightData()
        setBattlePassState(self.viewModel)
        self.__comp7LightController.onStatusTick += self.__onDataChange
        self.__comp7LightController.onModeConfigChanged += self.__onDataChange

    def _onDisposing(self):
        self.__comp7LightController.onStatusTick -= self.__onDataChange
        self.__comp7LightController.onModeConfigChanged -= self.__onDataChange
        super(Comp7LightModeSelectorItem, self)._onDisposing()

    def __onDataChange(self):
        self.__updateComp7LightData()
        self.onCardChange()

    def __updateComp7LightData(self):
        self.__fillModeData()
        self.__fillWidgetData()

    def __getCurrentSeasonTimeLeft(self, currentSeason):
        return time_formatters.getTillTimeByResource(max(0, currentSeason.getEndDate() - time_utils.getServerUTCTime()), R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True)

    def __fillModeData(self):
        currentSeason = self.__comp7LightController.getCurrentSeason()
        isSeasonAvailable = self.__comp7LightController.isAvailable() and currentSeason is not None
        with self.viewModel.transaction() as vm:
            if isSeasonAvailable:
                vm.setTimeLeft(self.__getCurrentSeasonTimeLeft(currentSeason))
                self._addReward(ModeSelectorRewardID.CREDITS)
                self._addReward(ModeSelectorRewardID.EXPERIENCE)
                vm.setDescription(backport.text(R.strings.mode_selector.mode.comp7Light.description(), tier=int2roman(self.__comp7LightController.getModeSettings().levels[0])))
            vm.setExternalPath(R.views.comp7_light.lobby.Comp7LightBattleCard())
        return

    def __fillWidgetData(self):
        with self.viewModel.widget.transaction() as vm:
            if not self.__comp7LightProgressionController.isEnabled:
                self.viewModel.widget.setStatus(Comp7LightProgressionStatus.DISABLED)
                return
            data = self.__comp7LightProgressionController.getCurrentStageData()
            vm.setStatus(Comp7LightProgressionStatus.ACTIVE)
            vm.setCurrentStage(data['currentStage'])
            vm.setStageCurrentPoints(data['stagePoints'])
            vm.setStageMaximumPoints(data['stageMaxPoints'])
