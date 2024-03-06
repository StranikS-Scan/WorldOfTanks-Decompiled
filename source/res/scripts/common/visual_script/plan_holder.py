# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/plan_holder.py
from debug_utils import LOG_ERROR

class PlanHolder(object):
    __slots__ = ('plan', 'loadState', 'autoStart', '__inputParamCache', 'params')
    INACTIVE = 0
    LOADING = 1
    LOADED = 2
    ERROR = 3
    LOAD_CANCELED = 4

    def __init__(self, plan, state, auto=False):
        self.plan = plan
        self.loadState = state
        self.autoStart = auto
        self.__inputParamCache = {}
        self.params = {}

    @property
    def isLoaded(self):
        return self.loadState == PlanHolder.LOADED

    @property
    def isError(self):
        return self.loadState == PlanHolder.ERROR

    @property
    def isLoadCanceled(self):
        return self.loadState == PlanHolder.LOAD_CANCELED

    def load(self, planName, aspect, tags):
        if self.loadState == PlanHolder.LOADING:
            if self.plan.load(planName, aspect, tags):
                self.loadState = PlanHolder.LOADED
            elif self.plan.isLoadCanceled():
                self.loadState = PlanHolder.LOAD_CANCELED
            else:
                LOG_ERROR('[VScript] PlanHolder: Can not load plan - %s' % planName)
                self.loadState = PlanHolder.ERROR
            if self.isLoaded:
                self._fetchInputParams()
            if self.autoStart:
                self.start()

    def start(self):
        if self.isLoaded:
            self.plan.start(self.params)

    def _fetchInputParams(self):
        for name, value in self.__inputParamCache.iteritems():
            self.plan.setOptionalInputParam(name, value)

        self.__inputParamCache.clear()

    def setOptionalInputParam(self, name, value):
        if self.isLoaded:
            self.plan.setOptionalInputParam(name, value)
            return
        self.__inputParamCache[name] = value

    def setOptionalInputParams(self, **kwargs):
        if self.isLoaded:
            for k, v in kwargs.iteritems():
                self.plan.setOptionalInputParam(k, v)

            return
        self.__inputParamCache.update(kwargs)
