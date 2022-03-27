# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/epic_mode_selector_item.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.formatters import time_formatters
from gui.shared.formatters.ranges import toRomanRangeString
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import BattlePassState
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class EpicModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.EPIC_BATTLE
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

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

    def __onEventEnded(self):
        self.onCardChange()

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            self.__resetViewModel(vm)
            currentSeason = self.__epicController.getCurrentSeason()
            nextSeason = self.__epicController.getNextSeason()
            season = currentSeason or nextSeason
            currentTime = time_utils.getCurrentLocalServerTimestamp()
            vm.setConditions(backport.text(R.strings.mode_selector.mode.epicBattle.condition(), levels=toRomanRangeString(self.__epicController.getValidVehicleLevels())))
            vm.setDescription(backport.text(R.strings.mode_selector.mode.epicBattle.description()))
            if season is None:
                return
            if season.hasActiveCycle(currentTime):
                self._addReward(ModeSelectorRewardID.CREDITS)
                self._addReward(ModeSelectorRewardID.EXPERIENCE)
                timeLeftStr = ''
                cycleInfo = season.getCycleInfo()
                if cycleInfo is not None:
                    timeLeftStr = time_formatters.getTillTimeByResource(cycleInfo.endDate - currentTime, R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True)
                vm.setTimeLeft(timeLeftStr)
            else:
                cycleInfo = season.getNextByTimeCycle(currentTime)
                if cycleInfo is not None:
                    if cycleInfo.announceOnly:
                        vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.epicBattle.cycleSoon()))
                    else:
                        vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.epicBattle.cycleNext(), date=backport.getShortDateFormat(cycleInfo.startDate)))
                    self.viewModel.setBattlePassState(BattlePassState.NONE)
                else:
                    vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.epicBattle.seasonEnd()))
        setBattlePassState(self.viewModel)
        return

    @staticmethod
    def __resetViewModel(vm):
        vm.setTimeLeft('')
        vm.setStatusActive('')
        vm.setStatusNotActive('')
        vm.getRewardList().clear()
