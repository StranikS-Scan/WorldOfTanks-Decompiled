# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/multi_plan_provider.py
import VSE
from context import VScriptContext
from misc import preloadPlanXml
from typing import Iterable, Any
from debug_utils import LOG_ERROR
from plan_tags import PlanTags
from constants import IS_DEVELOPMENT
from soft_exception import SoftException

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
        return self.loadState is PlanHolder.LOADED

    @property
    def isError(self):
        return self.loadState is PlanHolder.ERROR

    @property
    def isLoadCanceled(self):
        return self.loadState is PlanHolder.LOAD_CANCELED

    @preloadPlanXml
    def load(self, planName, aspect, tags):
        if self.loadState is PlanHolder.LOADING:
            if self.plan.load(planName, aspect, tags):
                self.loadState = PlanHolder.LOADED
            elif self.plan.isLoadCanceled():
                self.loadState = PlanHolder.LOAD_CANCELED
            else:
                LOG_ERROR('[VScript] MultiPlanProvider: Can not load plan - %s', planName)
                self.loadState = PlanHolder.ERROR
            if self.isLoaded:
                for name, value in self.__inputParamCache.iteritems():
                    self.plan.setOptionalInputParam(name, value)

                self.__inputParamCache.clear()
            if self.autoStart:
                self.start()

    def start(self):
        if self.isLoaded:
            self.plan.start(self.params)

    def setOptionalInputParam(self, name, value):
        if self.isLoaded:
            self.plan.setOptionalInputParam(name, value)
            return
        self.__inputParamCache[name] = value


class MultiPlanProvider(object):

    def __init__(self, aspect, arenaBonusType=0):
        self._plans = {}
        self._aspect = aspect
        self._context = None
        self._planTags = PlanTags(arenaBonusType)
        return

    def destroy(self):
        pass

    def reset(self):
        self.stop()
        for holder in self._plans.itervalues():
            holder.loadState = PlanHolder.INACTIVE

        self._plans = {}
        self._context = None
        return

    def get(self, planName):
        return self._plans.get(planName, PlanHolder(None, PlanHolder.INACTIVE)).plan

    def start(self):
        for holder in self._plans.itervalues():
            if holder.isLoaded:
                holder.plan.start(holder.params)
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
                holder.plan.start(holder.params)

    def pause(self):
        map(lambda holder: holder.plan.pause() if holder.isLoaded else None, self._plans.itervalues())

    def isLoaded(self):
        return all((holder.isLoaded or holder.isLoadCanceled for holder in self._plans.itervalues()))

    def isError(self):
        return any((holder.isError for holder in self._plans.itervalues()))

    def load(self, planNames, autoStart=False):
        self.reset()
        for entry in planNames:
            if isinstance(entry, dict):
                self._loadPlan(entry['name'], dict(entry['params']))
            self._loadPlan(entry)

    def startPlan(self, planName, params={}):
        self._loadPlan(planName, params, True)

    def setOptionalInputParam(self, name, value):
        for holder in self._plans.itervalues():
            holder.setOptionalInputParam(name, value)

    def setContext(self, context):
        for holder in self._plans.itervalues():
            holder.plan.setContext(context)

        self._context = context

    def _loadPlan(self, planName, params={}, autoStart=False):
        holder = PlanHolder(VSE.Plan(), PlanHolder.LOADING, autoStart)
        holder.params = params
        if self._context is not None:
            holder.plan.setContext(self._context)
        holder.load(planName, self._aspect, self._planTags.tags)
        self._plans[planName] = holder
        return holder


class CallableProviderType:
    ARENA = 'ARENA'
    HANGAR = 'HANGAR'
    DEATH_ZONES = 'DEATH_ZONES'
    LOOT = 'LOOT'


if IS_DEVELOPMENT:

    class CallablePlanProvider(MultiPlanProvider):
        providers = {CallableProviderType.ARENA: set(),
         CallableProviderType.HANGAR: set(),
         CallableProviderType.DEATH_ZONES: set(),
         CallableProviderType.LOOT: set()}
        plansOnLoad = dict()

        def __init__(self, aspect, name, arenaBonusType=0):
            super(CallablePlanProvider, self).__init__(aspect, arenaBonusType)
            self._name = name
            self.providers.setdefault(name, set()).add(self)

        def destroy(self):
            self.providers[self._name].remove(self)

        def load(self, planNames, autoStart=False):
            super(CallablePlanProvider, self).load(planNames, autoStart)
            if self._name in self.plansOnLoad:
                for entry in self.plansOnLoad[self._name]:
                    if isinstance(entry, dict):
                        self._loadPlan(entry['name'], dict(entry['params']), autoStart)
                    self._loadPlan(entry, {}, autoStart)


    def setPlansOnLoad(name, planNames):
        CallablePlanProvider.plansOnLoad[name] = planNames


    def startPlan(name, planName, params={}):
        if name not in CallablePlanProvider.providers:
            raise SoftException('Wrong provider name')
        for provider in CallablePlanProvider.providers[name]:
            provider.startPlan(planName, params)


def makeMultiPlanProvider(aspect, name, arenaBonusType=0):
    return CallablePlanProvider(aspect, name, arenaBonusType) if IS_DEVELOPMENT else MultiPlanProvider(aspect, arenaBonusType)
