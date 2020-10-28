# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/multi_plan_provider.py
import VSE
from misc import preloadPlanXml
from typing import Iterable
from debug_utils import LOG_ERROR

class PlanHolder(object):
    __slots__ = ('plan', 'loadState', 'autoStart', '__inputParamCache')
    INACTIVE = 0
    LOADING = 1
    LOADED = 2

    def __init__(self, plan, state, auto=False):
        self.plan = plan
        self.loadState = state
        self.autoStart = auto
        self.__inputParamCache = {}

    @property
    def isLoaded(self):
        return self.loadState is PlanHolder.LOADED

    @preloadPlanXml
    def load(self, planName, aspect):
        if self.loadState is PlanHolder.LOADING:
            if self.plan.load(planName, aspect):
                self.loadState = PlanHolder.LOADED
            else:
                LOG_ERROR('[VScript] MultiPlanProvider: Can not load plan - %s', planName)
            if self.isLoaded:
                for name, value in self.__inputParamCache.iteritems():
                    self.plan.setOptionalInputParam(name, value)

                self.__inputParamCache.clear()
            if self.isLoaded and self.autoStart:
                self.plan.start()

    def setOptionalInputParam(self, name, value):
        if self.loadState == PlanHolder.LOADED:
            self.plan.setOptionalInputParam(name, value)
            return
        self.__inputParamCache[name] = value


class MultiPlanProvider(object):

    def __init__(self, aspect):
        self._plans = {}
        self._aspect = aspect

    def reset(self):
        self.stop()
        for holder in self._plans.itervalues():
            holder.loadState = PlanHolder.INACTIVE

        self._plans = {}

    def get(self, planName):
        return self._plans.get(planName, PlanHolder(None, PlanHolder.INACTIVE)).plan

    def start(self):
        for holder in self._plans.itervalues():
            if holder.isLoaded:
                holder.plan.start()
            holder.autoStart = True

    def stop(self):
        for holder in self._plans.itervalues():
            if holder.isLoaded:
                holder.plan.stop()
            holder.autoStart = False

    def restart(self):
        for holder in self._plans.itervalues():
            if holder.isLoaded:
                holder.plan.stop()
                holder.plan.start()

    def pause(self):
        map(lambda holder: holder.plan.pause() if holder.isLoaded else None, self._plans.itervalues())

    def isLoaded(self):
        return all((holder.isLoaded for holder in self._plans.itervalues()))

    def load(self, planNames, autoStart=False):
        self.reset()
        for planName in planNames:
            holder = PlanHolder(VSE.Plan(), PlanHolder.LOADING, autoStart)
            holder.load(planName, self._aspect)
            self._plans[planName] = holder

    def setOptionalInputParam(self, name, value):
        for holder in self._plans.itervalues():
            holder.setOptionalInputParam(name, value)
