# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/simulator.py
import itertools
import math
from collections import defaultdict, deque
from debug_utils import LOG_DEBUG
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.events_handler import EventsHandler
from helpers.time_utils import ONE_MINUTE, getServerUTCTime
from math_common import isAlmostEqual
from new_year.ny_constants import TamagotchiState
from new_year.skeletons.new_year import ITamagotchiDataProvider
from wotdecorators import noexceptReturn
_TICK_TIME = float(ONE_MINUTE)

class TamagotchiSimulator(EventsHandler):
    __slots__ = ('__ticker',)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self):
        super(TamagotchiSimulator, self).__init__()
        self.__ticker = CallbackDelayer()

    def init(self):
        self._subscribe()

    def fini(self):
        self._unsubscribe()
        self.__ticker.clearCallbacks()

    def setEnabled(self, state):
        self._updateCallbacks(state)

    @classmethod
    def getDelayTime(cls):
        timeDiff = math.ceil(getServerUTCTime() - cls._dataProvider.initialPlayerInfo.lastUpdateTime)
        return _TICK_TIME - timeDiff % _TICK_TIME

    def _updateCallbacks(self, state):
        self.__ticker.clearCallbacks()
        if not state or not self._dataProvider.isValidConfig:
            return
        self.__recalcGift()
        giftDelay = self._dataProvider.getGiftDelay()
        if giftDelay > 0 or isAlmostEqual(giftDelay, 0):
            self.__ticker.delayCallback(giftDelay, self.__onGiftObtained)
            LOG_DEBUG('[TAMAGOTCHI update] next gift delay is ', self._dataProvider.getGiftDelay())
        self.__ticker.delayCallback(0, self.__tick)
        self.__ticker.delayCallback(0, self.__onDebUpdated)

    @noexceptReturn(_TICK_TIME)
    def __tick(self):
        timestamp = getServerUTCTime()
        self._dataProvider.getIndicatorStates().clear()
        for name, points in self._dataProvider.initialPlayerInfo.indicators.iteritems():
            if points < 0 or name not in self._dataProvider.config.indicators:
                continue
            self.__updateIndicator(name, points, timestamp)

        self.__updateState()
        LOG_DEBUG('[TAMAGOTCHI tick] ', self._dataProvider.playerInfo.state, self._dataProvider.playerInfo.indicators, self._dataProvider.getDeb())
        self._dataProvider.onSimulationEnd()
        return self.getDelayTime()

    def __updateIndicator(self, name, points, timestamp):
        sInfo = self._dataProvider.playerInfo
        states = self._dataProvider.getIndicatorStates()
        decayConfig = self._dataProvider.config.indicators[name]
        timeDiff = max(0, timestamp - self._dataProvider.initialPlayerInfo.lastUpdateTime)
        minutesDiff = math.floor(timeDiff / _TICK_TIME)
        state = 0
        for level in reversed(decayConfig.levels):
            if points < level.points:
                continue
            minutesToDecay = (points - level.points) / level.degradation
            if minutesToDecay > minutesDiff:
                points = points - level.degradation * minutesDiff
                state = level.state
                break
            points = level.points
            minutesDiff -= minutesToDecay

        sInfo.indicators[name] = points
        states[name] = state

    def __updateState(self):
        score = maxScore = 0
        for name, value in self._dataProvider.getIndicatorStates().iteritems():
            score += value
            maxScore += self._dataProvider.config.indicators[name].levels[-1].state

        if score == 0:
            self._dataProvider.playerInfo.state = TamagotchiState.SAD.value
            return
        if score == maxScore:
            self._dataProvider.playerInfo.state = TamagotchiState.FUN.value
            return
        self._dataProvider.playerInfo.state = TamagotchiState.NORMAL.value

    def __onDebUpdated(self):
        clientTime = getServerUTCTime()
        history = self._dataProvider.playerInfo.debHistory
        diff = -1
        while history:
            top = history[0]
            diff = top.expirationTime - clientTime
            if diff > 0:
                break
            history.popleft()

        if diff > 0:
            self._dataProvider.onBonusUpdated()
        return diff

    def __recalcGift(self):
        sInfo = self._dataProvider.playerInfo
        timestamp = getServerUTCTime()
        sInfo.giftCount, sInfo.giftTime = self.__recalcGiftTime(timestamp)
        if sInfo.giftTime > 0:
            sInfo.giftTime += timestamp

    @noexceptReturn(0)
    def __onGiftObtained(self):
        self.__recalcGift()
        self._dataProvider.onGiftCountUpdated()
        LOG_DEBUG('[TAMAGOTCHI callback] next gift delay is ', self._dataProvider.getGiftDelay())
        return self._dataProvider.getGiftDelay()

    def __getFactorsDecayHist(self):
        pInfo = self._dataProvider.initialPlayerInfo
        decayHist = defaultdict(dict)
        currentFactors = dict()
        for name, points in pInfo.indicators.iteritems():
            absMinutesLeft = 0
            points = pInfo.indicators[name]
            if points < 0:
                currentFactors[name] = 0.0
                continue
            levels = self._dataProvider.config.indicators[name].levels
            currIt, nextIt = itertools.tee(reversed(levels))
            next(nextIt, None)
            for item in currIt:
                diff = points - item.points
                nextItem = next(nextIt, levels[0])
                if diff < 0:
                    continue
                minutesToDecay = int(math.ceil(diff / item.degradation))
                points = item.points
                absMinutesLeft += minutesToDecay
                decayHist[absMinutesLeft][name] = nextItem.giftSpeedFactor
                if name not in currentFactors:
                    currentFactors[name] = item.giftSpeedFactor

        return (currentFactors, decayHist)

    def __recalcGiftTime(self, timestamp):
        currentFactors, decayHist = self.__getFactorsDecayHist()
        decayQueue = deque(sorted(decayHist))
        count = len(currentFactors)
        baseTime = self._dataProvider.initialPlayerInfo.giftTime
        giftCount = self._dataProvider.initialPlayerInfo.giftCount
        minutesDiff = 0
        updateTime = self._dataProvider.initialPlayerInfo.lastUpdateTime
        baseMinutesToGift = baseTime / _TICK_TIME
        while decayQueue:
            minutesToDecay = decayQueue[0]
            factor = 1 + sum(currentFactors.values()) / count
            timeShift = (minutesToDecay - minutesDiff) * factor
            if timeShift >= baseMinutesToGift:
                realMinutesToGift = baseMinutesToGift / factor
                roundDelta = math.ceil(realMinutesToGift)
                extraTime = (roundDelta - realMinutesToGift) * factor * _TICK_TIME
                giftTime = (realMinutesToGift + minutesDiff) * _TICK_TIME + updateTime - timestamp
                if giftTime > 0 and not isAlmostEqual(giftTime, 0):
                    return (giftCount, giftTime)
                minutesDiff += roundDelta
                baseTime = max(0, self._dataProvider.config.gift.baseInterval - extraTime)
                baseMinutesToGift = baseTime / _TICK_TIME
                giftCount += 1
                continue
            currentFactors.update(decayHist[minutesToDecay])
            minutesDiff = minutesToDecay
            baseMinutesToGift -= timeShift
            decayQueue.popleft()

        return (giftCount, 0)
