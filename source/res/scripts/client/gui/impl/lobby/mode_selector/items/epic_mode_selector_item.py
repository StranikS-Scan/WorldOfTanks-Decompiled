# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/epic_mode_selector_item.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_epic_model import ModeSelectorEpicModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.event_dispatcher import showFrontlineInfoWindow
from gui.shared.formatters import time_formatters
from gui.shared.formatters.ranges import toRomanRangeString, toRangeString
from gui.shared.utils import isRomanNumberForbidden
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ('_isNew', '_battleType')
    _VIEW_MODEL = ModeSelectorEpicModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.EPIC_BATTLE
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, oldSelectorItem):
        super(EpicModeSelectorItem, self).__init__(oldSelectorItem)
        self._battleType = SELECTOR_BATTLE_TYPES.EPIC
        self._isNew = not selectorUtils.isKnownBattleType(self._battleType)

    @property
    def isVisible(self):
        return self.__epicController.isEnabled() and self.__epicController.getCurrentSeasonID()

    def _getIsDisabled(self):
        return not self.__epicController.isEnabled()

    def _onInitializing(self):
        super(EpicModeSelectorItem, self)._onInitializing()
        self.__epicController.onPrimeTimeStatusUpdated += self.__onEpicUpdate
        self.__epicController.onUpdated += self.__onEpicUpdate
        self.__epicController.onEventEnded += self.__onEventEnded
        self.__fillViewModel()

    def _onDisposing(self):
        self.__epicController.onPrimeTimeStatusUpdated -= self.__onEpicUpdate
        self.__epicController.onUpdated -= self.__onEpicUpdate
        self.__epicController.onEventEnded -= self.__onEventEnded
        super(EpicModeSelectorItem, self)._onDisposing()

    def __onEpicUpdate(self, *_):
        self.__fillViewModel()
        self.onCardChange()
        self.__epicController.onGameModeStatusTick()

    def __onEventEnded(self):
        self.onCardChange()

    def _isInfoIconVisible(self):
        return True

    def handleClick(self):
        self.__epicController.showProgressionDuringSomeStates(True)

    @property
    def isSelectable(self):
        from frontline.gui.frontline_helpers import isHangarAvailable
        return isHangarAvailable()

    def handleInfoPageClick(self):
        showFrontlineInfoWindow()
        if self._isNew:
            selectorUtils.setBattleTypeAsKnown(self._battleType)

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            self.__resetViewModel(vm)
            season = self.__epicController.getActiveSeason()
            currentTime = time_utils.getCurrentLocalServerTimestamp()
            vehicleLevels = self.__epicController.getValidVehicleLevels()
            localeFolder = R.strings.mode_selector.mode.epicBattle
            vm.setConditions(str(backport.text(localeFolder.conditionSingleLevel() if len(vehicleLevels) == 1 else localeFolder.condition(), levels=toRangeString(vehicleLevels) if isRomanNumberForbidden() else toRomanRangeString(vehicleLevels))))
            vm.setDescription(str(backport.text(R.strings.mode_selector.mode.epicBattle.description())))
            if season is None:
                return
            vm.widget.setIsEnabled(True)
            vm.widget.setRestRewards(self.__epicController.getNotChosenRewardCount())
            currentLevel, levelProgress = self.__epicController.getPlayerLevelInfo()
            if season.hasActiveCycle(currentTime):
                self._addReward(ModeSelectorRewardID.CREDITS)
                self._addReward(ModeSelectorRewardID.EXPERIENCE)
                timeLeftStr = ''
                cycleInfo = season.getCycleInfo()
                if cycleInfo is not None:
                    timeLeftStr = time_formatters.getTillTimeByResource(cycleInfo.endDate - currentTime, R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True)
                vm.setTimeLeft(timeLeftStr)
                vm.widget.setLevel(currentLevel)
            else:
                cycleInfo = season.getNextByTimeCycle(currentTime)
                if cycleInfo is not None:
                    if cycleInfo.announceOnly:
                        vm.setStatusNotActive(str(backport.text(R.strings.mode_selector.mode.epicBattle.cycleSoon())))
                    else:
                        vm.setStatusNotActive(str(backport.text(R.strings.mode_selector.mode.epicBattle.cycleNext(), date=backport.getShortDateFormat(cycleInfo.startDate))))
                    self.viewModel.setBattlePassState(BattlePassState.NONE)
                else:
                    vm.setStatusNotActive(str(backport.text(R.strings.mode_selector.mode.epicBattle.seasonEnd())))
                if currentLevel > 1 or levelProgress > 0:
                    vm.widget.setLevel(currentLevel)
        setBattlePassState(self.viewModel)
        return

    @staticmethod
    def __resetViewModel(vm):
        vm.setTimeLeft('')
        vm.setStatusActive('')
        vm.setStatusNotActive('')
        vm.getRewardList().clear()
