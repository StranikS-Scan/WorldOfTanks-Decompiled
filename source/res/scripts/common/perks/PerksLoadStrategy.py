# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/perks/PerksLoadStrategy.py
from perks.vse_plan import VsePlan, PlanStatus
from wg_async import wg_async, wg_await, distributeLoopOverTicks

class LoadType:
    DEFAULT = 0
    AUTO_START = 1
    DELAYED_LOAD_START = 2


class LoadState:
    DEFAULT = 0
    PRE_LOAD = 1
    LOAD = 2
    PRE_START = 3
    START = 4
    STATUS_LOADED = (LOAD, PRE_START, START)


class BaseLoadStrategy(object):

    def __init__(self, plans, scope, owner, onPlanReady):
        self._plans = plans
        self._scope = scope
        self._owner = owner
        self._state = None
        self._onPlansReady = onPlanReady
        self._setState(LoadState.DEFAULT)
        return

    def load(self):
        pass

    def start(self):
        pass

    def beforeBattleStart(self):
        pass

    @property
    def state(self):
        return self._state

    def _setState(self, value):
        if self._state != value:
            self._state = value
            self._stateLogic()

    def _stateLogic(self):
        if self._state == LoadState.START:
            self._onReady()

    def _onStatusChanged(self):
        pass

    def _checkIsAllPlansReady(self):
        return all((plan.isPlanStarted for plan in self._plans))

    def _checkIsAllPlansLoaded(self):
        return all((plan.status == PlanStatus.LOAD for plan in self._plans))

    def _clearPlansCallback(self):
        for plan in self._plans:
            plan._clearCallBack()

    def _onReady(self):
        self._clearPlansCallback()
        self._plans = []
        self._scope = []
        self._setState(LoadState.DEFAULT)
        self._onPlansReady()


class DefaultLoadStrategy(BaseLoadStrategy):

    def load(self):
        self._setState(LoadState.PRE_LOAD)

    def start(self):
        if self._state == LoadState.PRE_LOAD:
            self._setState(LoadState.PRE_START)

    @wg_async
    def loadPlansAsync(self, isAutoStart=False):
        _MAX_LOAD_PLANS = 10
        tempCreator = []
        for scopeId, (scope, creator) in self._scope.iteritems():
            for perkId, (level, args) in scope:
                plan = VsePlan(self._owner, scopeId, level, perkId, self._onStatusChanged, args)
                self._plans.append(plan)
                tempCreator.append(creator)

        def asyncLoop():
            for idx, item in enumerate(self._plans):
                yield item.load(tempCreator[idx], isAutoStart)

        yield wg_await(distributeLoopOverTicks(asyncLoop(), maxPerTick=_MAX_LOAD_PLANS, logID='loadPlans'))

    @wg_async
    def _startAsync(self):

        def asyncLoop():
            for plan in self._plans:
                yield plan.start()

        yield wg_await(distributeLoopOverTicks(asyncLoop(), maxPerTick=1, logID='start'))

    def _onStatusChanged(self):
        if self._state == LoadState.PRE_START:
            if self._checkIsAllPlansReady():
                self._setState(LoadState.START)

    def _stateLogic(self):
        if self._state == LoadState.PRE_LOAD:
            self.loadPlansAsync()
            return
        if self._state == LoadState.PRE_START:
            self._startAsync()
            return
        super(DefaultLoadStrategy, self)._stateLogic()


class AutoStartStrategy(DefaultLoadStrategy):

    def start(self):
        pass

    def load(self):
        self._setState(LoadState.PRE_LOAD)

    def _stateLogic(self):
        if self._state == LoadState.PRE_LOAD:
            self.loadPlansAsync(True)
            return
        super(AutoStartStrategy, self)._stateLogic()

    def _onStatusChanged(self):
        if self._state == LoadState.PRE_LOAD:
            if self._checkIsAllPlansReady():
                self._setState(LoadState.START)


class DelayLoadStartStrategy(DefaultLoadStrategy):

    def __init__(self, plans, scope, owner, onPlanReady):
        self._isStarted = False
        super(DelayLoadStartStrategy, self).__init__(plans, scope, owner, onPlanReady)

    def load(self):
        pass

    def start(self):
        pass

    def beforeBattleStart(self):
        if self._isStarted:
            return
        if self._state == LoadState.DEFAULT:
            self._setState(LoadState.PRE_LOAD)

    def _onStatusChanged(self):
        if self._state == LoadState.PRE_LOAD:
            if self._checkIsAllPlansLoaded():
                self._setState(LoadState.PRE_START)
                return
        if self._state == LoadState.PRE_START:
            if self._checkIsAllPlansReady():
                self._setState(LoadState.START)

    def _stateLogic(self):
        if self._state == LoadState.PRE_LOAD:
            self._isStarted = True
            self.loadPlansAsync()
            return
        super(DelayLoadStartStrategy, self)._stateLogic()


BUILDER = {LoadType.DEFAULT: DefaultLoadStrategy,
 LoadType.AUTO_START: AutoStartStrategy,
 LoadType.DELAYED_LOAD_START: DelayLoadStartStrategy}

def getLoadStarategy(value):
    return BUILDER.get(value)
