# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/battle_royale_mode_selector_item.py
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_battle_royale_model import ModeSelectorBattleRoyaleModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_battle_royale_widget_model import BattleRoyaleProgressionStatus
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBattleRoyaleController
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController

class BattleRoyaleModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorBattleRoyaleModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.BATTLE_ROYALE
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    brProgression = dependency.descriptor(IBRProgressionOnTokensController)

    @property
    def viewModel(self):
        return super(BattleRoyaleModeSelectorItem, self).viewModel

    @property
    def hasExtendedCalendarTooltip(self):
        return True

    def getExtendedCalendarTooltip(self, parentWindow):
        return createAndLoadBackportTooltipWindow(parentWindow, tooltipId=TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SELECTOR_CALENDAR_INFO, isSpecial=True, specialArgs=(None,))

    def _urlProcessing(self, url):
        return GUI_SETTINGS.checkAndReplaceWebBridgeMacros(url)

    def _onInitializing(self):
        super(BattleRoyaleModeSelectorItem, self)._onInitializing()
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.__onUpdate
        self.__battleRoyaleController.onUpdated += self.__onUpdate
        self.brProgression.onProgressPointsUpdated += self.__fillWidgetData
        self.brProgression.onSettingsChanged += self.__fillWidgetData
        self.__onUpdate()

    def _onDisposing(self):
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.__onUpdate
        self.__battleRoyaleController.onUpdated -= self.__onUpdate
        self.brProgression.onProgressPointsUpdated -= self.__fillWidgetData
        self.brProgression.onSettingsChanged -= self.__fillWidgetData
        super(BattleRoyaleModeSelectorItem, self)._onDisposing()

    def _getIsDisabled(self):
        ctrl = self.__battleRoyaleController
        season = ctrl.getCurrentSeason() or ctrl.getNextSeason()
        return not (ctrl.isEnabled() and season is not None)

    def _isInfoIconVisible(self):
        return True

    def __onUpdate(self, *_):
        self.__fillViewModel()
        self.__fillWidgetData()

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            season = self.__battleRoyaleController.getCurrentSeason() or self.__battleRoyaleController.getNextSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            if season is None:
                return
            self.__resetViewModel(vm)
            if season.hasActiveCycle(currTime):
                if self.__battleRoyaleController.isEnabled():
                    timeLeftStr = time_utils.getTillTimeString(season.getCycleEndDate() - currTime, EPIC_BATTLE.STATUS_TIMELEFT, removeLeadingZeros=True)
                    vm.setTimeLeft(timeLeftStr)
                    self._addReward(ModeSelectorRewardID.CREDITS)
                    self._addReward(ModeSelectorRewardID.OTHER)
            else:
                cycleInfo = season.getNextByTimeCycle(currTime)
                if cycleInfo is not None:
                    if cycleInfo.announceOnly:
                        text = backport.text(R.strings.battle_royale.modeSelector.cycleIsComing())
                    else:
                        text = backport.text(R.strings.battle_royale.modeSelector.cycleNotStarted(), date=backport.getShortDateFormat(cycleInfo.startDate))
                    vm.setStatusNotActive(text)
                    vm.setTimeLeft('')
            setBattlePassState(self.viewModel)
        return

    @staticmethod
    def __resetViewModel(vm):
        vm.setTimeLeft('')
        vm.setStatusActive('')
        vm.setStatusNotActive('')
        vm.setEventName('')
        vm.getRewardList().clear()

    def __fillWidgetData(self):
        if not self.brProgression.isEnabled:
            with self.viewModel.widget.transaction() as vm:
                vm.setStatus(BattleRoyaleProgressionStatus.DISABLED)
            return
        data = self.brProgression.getCurrentStageData()
        with self.viewModel.widget.transaction() as vm:
            vm.setStatus(BattleRoyaleProgressionStatus.ACTIVE)
            vm.setCurrentStage(data['currentStage'])
            vm.setStageCurrentPoints(data['stagePoints'])
            vm.setStageMaximumPoints(data['stageMaxPoints'])
