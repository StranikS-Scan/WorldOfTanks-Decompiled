# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_sub_modes_info.py
import typing
from fun_random.gui.feature.fun_constants import FunSubModesState, STATE_TO_SINGLE
from fun_random.gui.feature.util.fun_helpers import mergeIntervals
from fun_random.gui.feature.models.common import FunSubModesStatus
from helpers import time_utils
from shared_utils import first
from skeletons.gui.game_control import IFunRandomController
from gui.periodic_battles.models import PeriodType
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
_INNER_END_PERIODS = (PeriodType.ALL_NOT_AVAILABLE_END, PeriodType.STANDALONE_NOT_AVAILABLE_END)
_OUTSIDE_PERIODS = (PeriodType.BEFORE_SEASON, PeriodType.BETWEEN_SEASONS, PeriodType.AFTER_SEASON)
_NO_BATTLES_PERIODS = _INNER_END_PERIODS + (PeriodType.AFTER_CYCLE,)

class FunSubModesInfo(IFunRandomController.IFunSubModesInfo):

    def __init__(self, subModesHolder):
        self.__subModes = subModesHolder

    def fini(self):
        self.__subModes = None
        return

    def isAvailable(self):
        return any([ subMode.isAvailable() for subMode in self.__subModes.getSubModes() ])

    def isEntryPointAvailable(self):
        isAvailable = self.getSubModesStatus().state not in FunSubModesState.HIDDEN_ENTRY_STATES
        return isAvailable and any([ subMode.isEntryPointAvailable() for subMode in self.__subModes.getSubModes() ])

    def getLeftTimeToPrimeTimesEnd(self, now=None, subModes=None):
        now = now or time_utils.getCurrentTimestamp()
        subModes = subModes if subModes is not None else self.__subModes.getSubModes()
        timesLeft = (sm.getLeftTimeToPrimeTimesEnd(now) for sm in subModes)
        timesLeft = tuple((timeLeft for timeLeft in timesLeft if timeLeft > 0))
        return min(timesLeft) if timesLeft else 0

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        subModes = self.__subModes.getSubModes()
        allPrimeTimes = [ sm.getPrimeTimesForDay(selectedTime, groupIdentical) for sm in subModes ]
        return first(allPrimeTimes) if len(subModes) == 1 else mergeIntervals(allPrimeTimes)

    def getSubModesStatus(self, subModesIDs=None):
        subModes = self.__subModes.getSubModes(subModesIDs)
        if not subModes:
            return FunSubModesStatus(FunSubModesState.UNDEFINED)
        else:
            now = time_utils.getCurrentTimestamp()
            periodInfos = tuple((subMode.getPeriodInfo(now) for subMode in subModes))
            if all((periodInfo.periodType in _OUTSIDE_PERIODS for periodInfo in periodInfos)):
                state = FunSubModesState.BETWEEN_SEASONS
                nearestStartTimes = [ pInfo.seasonBorderRight.timestamp for pInfo in periodInfos if pInfo.seasonBorderRight ]
                if all((periodInfo.periodType == PeriodType.AFTER_SEASON for periodInfo in periodInfos)):
                    state = FunSubModesState.AFTER_SEASON
                elif all((periodInfo.periodType == PeriodType.BEFORE_SEASON for periodInfo in periodInfos)):
                    state = FunSubModesState.BEFORE_SEASON
                return FunSubModesStatus(state, min(nearestStartTimes) if nearestStartTimes else None)
            state = FunSubModesState.AVAILABLE
            periodInfos = tuple((pInfo for pInfo in periodInfos if pInfo.periodType not in _OUTSIDE_PERIODS))
            latestEndTime = max([ pInfo.seasonBorderRight.timestamp for pInfo in periodInfos ])
            primeDelta = time_utils.getTimeDeltaFromNowInLocal(latestEndTime)
            if all((periodInfo.periodType in _NO_BATTLES_PERIODS for periodInfo in periodInfos)):
                state = FunSubModesState.NOT_AVAILABLE_END
            elif all((periodInfo.periodType == PeriodType.FROZEN for periodInfo in periodInfos)):
                state = FunSubModesState.FROZEN
            elif all((not sm.hasAvailablePrimeTimeServers(now) for sm in subModes)):
                state = FunSubModesState.NOT_AVAILABLE
                primeDelta = self.getLeftTimeToPrimeTimesEnd(now, subModes)
            if len(subModes) == 1:
                state = STATE_TO_SINGLE.get(state, state)
            return FunSubModesStatus(state, latestEndTime, primeDelta)
