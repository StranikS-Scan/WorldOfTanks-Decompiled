# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/multi_plan_provider.py
import VSE
from context import VScriptContext
from typing import Iterable, Any
from plan_tags import PlanTags
from constants import IS_DEVELOPMENT
from soft_exception import SoftException
from plan_holder import PlanHolder

class MultiPlanProvider(object):
    PLAN_KEY_SEPARATOR = '#'

    def __init__(self, aspect, arenaBonusType=0):
        self._plans = {}
        self._aspect = aspect
        self._context = None
        self._planTags = PlanTags(arenaBonusType)
        return

    def destroy(self):
        pass

    def getPlanNameWithKey(self, planName, key=''):
        nameWithKey = planName if key == '' else planName + self.PLAN_KEY_SEPARATOR + key
        return nameWithKey

    def reset(self):
        self.stop()
        for holder in self._plans.itervalues():
            holder.loadState = PlanHolder.INACTIVE

        self._plans = {}
        self._context = None
        return

    def get(self, planName, key=''):
        nameWithKey = self.getPlanNameWithKey(planName, key)
        return self._plans.get(nameWithKey, PlanHolder(None, PlanHolder.INACTIVE)).plan

    def start(self):
        for holder in self._plans.itervalues():
            holder.setOptionalInputParams(**holder.params)
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
            holder.setOptionalInputParams(**holder.params)
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
                self._loadPlan(entry['name'], dict(entry['params']), False, entry.get('plan_id', ''))
            self._loadPlan(entry)

    def startPlan(self, planName, params={}, key='', contextInstance=None):
        self._loadPlan(planName, params, True, key, contextInstance)

    def stopPlan(self, planName, key=''):
        nameWithKey = self.getPlanNameWithKey(planName, key)
        if nameWithKey in self._plans.keys():
            holder = self._plans[nameWithKey]
            if holder.isLoaded:
                holder.plan.stop()
            holder.autoStart = False

    def setOptionalInputParam(self, name, value):
        for holder in self._plans.itervalues():
            holder.setOptionalInputParam(name, value)

    def setOptionalInputParams(self, **kwargs):
        for holder in self._plans.itervalues():
            holder.setOptionalInputParams(**kwargs)

    def setContext(self, context):
        for holder in self._plans.itervalues():
            holder.plan.setContext(context)

        self._context = context

    def _loadPlan(self, planName, params={}, autoStart=False, key='', contextInstance=None):
        nameWithKey = self.getPlanNameWithKey(planName, key)
        holder = None
        if nameWithKey in self._plans.keys():
            holder = self._plans[nameWithKey]
            holder.params = params
            holder.autoStart = autoStart
            if holder.isLoaded and autoStart:
                holder.start()
        else:
            holder = PlanHolder(VSE.Plan(), PlanHolder.LOADING, autoStart)
            holder.params = params
            if contextInstance:
                holder.plan.setContext(contextInstance)
            elif self._context is not None:
                holder.plan.setContext(self._context)
            holder.load(planName, self._aspect, self._planTags.tags)
            self._plans[nameWithKey] = holder
        return holder


class CallableProviderType:
    ARENA = 'ARENA'
    HANGAR = 'HANGAR'
    DEATH_ZONES = 'DEATH_ZONES'
    LOOT = 'LOOT'
    ENTITY = 'ENTITY'


if IS_DEVELOPMENT:

    class CallablePlanProvider(MultiPlanProvider):
        providers = {CallableProviderType.ARENA: set(),
         CallableProviderType.HANGAR: set(),
         CallableProviderType.DEATH_ZONES: set(),
         CallableProviderType.LOOT: set(),
         CallableProviderType.ENTITY: set()}
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


class MultiPlanCache(object):

    def __init__(self, aspect):
        super(MultiPlanCache, self).__init__()
        self._plansBucket = {}
        self._aspect = aspect

    def destroy(self):
        for key, bucket in self._plansBucket.items():
            for vsePlans in bucket:
                vsePlans.stop()
                vsePlans.destroy()

        self._plansBucket.clear()

    def getPlan(self, componentName, planNamesAndParams):
        planNames = set(((entry['name'] if isinstance(entry, dict) else entry) for entry in planNamesAndParams))
        if componentName in self._plansBucket:
            for vsePlans in self._plansBucket[componentName]:
                if vsePlans.isLoaded() and all((not vsePlans.get(planName).isActive() for planName in planNames)):
                    return vsePlans

        vsePlans = makeMultiPlanProvider(self._aspect, componentName)
        vsePlans.load(planNamesAndParams)
        self._plansBucket.setdefault(componentName, []).append(vsePlans)
        return vsePlans
