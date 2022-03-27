# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/rts_mode_selector_item.py
import logging
import typing
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_rts_card_model import ModeSelectorRtsCardModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_rts_widget_model import ModeSelectorRtsWidgetModel
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRTSBattlesController, IRTSProgressionController
from gui.periodic_battles.models import PrimeTimeStatus
if typing.TYPE_CHECKING:
    from season_common import GameSeason
_logger = logging.getLogger(__name__)

def getTimeLeftFromSeason(season, currentTime):
    if not season.hasActiveCycle(currentTime):
        _logger.warning('getTimeLeftFromSeason: season has no active cycle')
        return
    else:
        cycleInfo = season.getCycleInfo()
        if cycleInfo is None:
            _logger.warning('getTimeLeftFromSeason: season cycle has no info')
            return
        seconds = cycleInfo.endDate - currentTime
        _logger.debug('getTimeLeftFromSeason: season end in %d seconds', seconds)
        return seconds


def isCycleActiveFromSeason(season, currentTime):
    if season is None:
        return False
    else:
        return False if not season.hasActiveCycle(currentTime) else True


class RTSModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.RTS
    _VIEW_MODEL = ModeSelectorRtsCardModel
    __rtsBattlesController = dependency.descriptor(IRTSBattlesController)
    __progressionCtrl = dependency.descriptor(IRTSProgressionController)

    @property
    def viewModel(self):
        return super(RTSModeSelectorItem, self).viewModel

    def handleInfoPageClick(self):
        self.__rtsBattlesController.showRTSInfoPage()

    def _getRtsNotActiveStatus(self):
        msR = R.strings.mode_selector.event
        rtsController = self.__rtsBattlesController
        currentSeason = rtsController.getCurrentSeason()
        if currentSeason is None:
            _logger.warning('RTSModeSelectorItem: no active season, selector item should be hidden')
            return ''
        else:
            now = _getNow()
            currentCycleInfo = currentSeason.getCycleInfo()
            if currentCycleInfo:
                if rtsController.hasAvailablePrimeTimeServers():
                    return ''
                hasPrimetimeLeft = rtsController.hasPrimeTimesLeftForCurrentCycle()
                if hasPrimetimeLeft:
                    return backport.text(msR.rts.paused())
                return backport.text(msR.rts.finished())
            nextCycle = currentSeason.getNextByTimeCycle(now)
            if nextCycle:
                return backport.text(msR.rts.notStarted())
            return backport.text(msR.rts.finished())
            return

    def _isInfoIconVisible(self):
        return True

    def _onInitializing(self):
        super(RTSModeSelectorItem, self)._onInitializing()
        self._addReward(ModeSelectorRewardID.OTHER)
        currentSeason = self.__rtsBattlesController.getCurrentSeason()
        currentTime = _getNow()
        isCycleActive = isCycleActiveFromSeason(currentSeason, currentTime)
        isBattlesPossible = self.__rtsBattlesController.isBattlesPossible()
        isPrimeTimeAvailable = self.__rtsBattlesController.getPrimeTimeStatus()[0] == PrimeTimeStatus.AVAILABLE
        timeLeft = ''
        if isCycleActive and isBattlesPossible and isPrimeTimeAvailable:
            timeLeft = getFormattedTimeLeft(getTimeLeftFromSeason(currentSeason, currentTime))
        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(timeLeft)
            vm.setStatusNotActive(self._getRtsNotActiveStatus())
            self._fillRTSWidget(vm.widget, isCycleActive)

    def _fillRTSWidget(self, model, isCycleActive):
        isEnabled = self.__progressionCtrl.isEnabled()
        currentProgress = self.__progressionCtrl.getCollectionProgress()
        totalProgress = self.__progressionCtrl.getCollectionSize()
        currentSeason = self.__rtsBattlesController.getCurrentSeason()
        now = _getNow()
        timeLeftToActive = 0
        if isCycleActive:
            if not self.__rtsBattlesController.hasAvailablePrimeTimeServers():
                nextPrimeTime = self.__rtsBattlesController.hasPrimeTimesLeftForCurrentCycle()
                if nextPrimeTime:
                    nextStartDate = nextPrimeTime.getNextPeriodStart(now, currentSeason.getCycleEndDate())
                    timeLeftToActive = nextStartDate - now
        else:
            nextCycle = currentSeason.getNextByTimeCycle(now)
            if nextCycle:
                timeLeftToActive = nextCycle.startDate - now
        with model.transaction() as vm:
            vm.setIsEnabled(isEnabled)
            vm.setIsProgressVisible(isCycleActive)
            vm.setCurrent(currentProgress)
            vm.setTotal(totalProgress)
            vm.setTimeLeftToActive(timeLeftToActive)
            vm.setIsCycleActive(isCycleActive)
            _logger.debug('__fillRTSWidget: progress: %d/%d isEnabled: %s isVisible: %s', currentProgress, totalProgress, isEnabled, isCycleActive)


def _getNow():
    return time_utils.getCurrentLocalServerTimestamp()
