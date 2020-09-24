# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/PerkPlanHolder.py
import BigWorld
import VSE
from copy import copy
from itertools import izip
from collections import defaultdict
from VSPlanEvents import SetPlanInitData, PLATOON_VS_PLAN_SIMPLE_EVENT
from constants import IS_CELLAPP
from debug_utils import LOG_ERROR
from items import perks
from visual_script.misc import ASPECT

class VsePlan(object):
    _PLAN_PATH = 'vscript/plans/{}.xml'
    _PLAN_STARTED_EVENT = 'planStarted'
    _PLAN_ID_PREFIX = 'abilityPerks/perk_'

    def __init__(self, owner, scopeId, level, perkId):
        self._owner = owner
        self.scopeId = scopeId
        self.perkId = perkId
        self._level = level
        self._planId = self._PLAN_ID_PREFIX + str(self.perkId)
        self._isPlanLoaded = False
        self._isPlanReady = False
        self._isAutoStart = False
        self._plan = None
        return

    def loadPlan(self, isAutoStart=False):
        self._isAutoStart = isAutoStart
        self._isPlanLoaded = False
        self._plan = VSE.Plan()
        valid, message = perks.g_cache.perks().validatePerk(self.perkId)
        if not valid:
            LOG_ERROR(message)
            return
        if IS_CELLAPP:
            future = BigWorld.resMgr.fetchDataSection(self._PLAN_PATH.format(self._planId))
            future.then(self._onPlanPreLoaded)
        else:
            self._onPlanPreLoaded()

    def setInputParam(self, paramName, paramValue):
        self._plan.setOptionalInputParam(paramName, paramValue)

    def _onPlanPreLoaded(self, future=None):
        try:
            if IS_CELLAPP:
                future.get()
            self._isPlanLoaded = self._plan.load(self._planId, (ASPECT.SERVER, ASPECT.CLIENT))
            if self._isAutoStart:
                self.start()
        except BigWorld.FutureNotReady:
            LOG_ERROR("Plan xml '%s' not pre-loaded." % self._planId)

    def start(self):
        if self._plan is not None:
            if not self._isPlanLoaded:
                self._isAutoStart = True
                return
            self._plan.subscribe(self._PLAN_STARTED_EVENT, SetPlanInitData(self._owner.id, self.scopeId, self.perkId, self._level), self._onStartEvent)
            self._plan.start()
        else:
            LOG_ERROR("Plan '%s' not created before start" % self._planId)
        return

    def restart(self):
        self.triggerVSPlanEvent(SetPlanInitData(self._owner.id, self.scopeId, self.perkId, self._level))

    def triggerVSPlanEvent(self, event):
        if isinstance(event, str):
            self._plan.triggerEvent(event)
        else:
            for key, value in izip(event._fields, event):
                self.setInputParam(key, value)

            self._plan.triggerEvent(event.__class__.__name__)

    def destroy(self):
        self._plan.stop()
        self._plan = None
        self._isPlanLoaded = False
        self._isPlanReady = False
        self._isAutoStart = False
        return

    def _onStartEvent(self, event):
        self._isPlanReady = True
        self.triggerVSPlanEvent(event)

    @property
    def isReady(self):
        return self._isPlanReady


class ImmediateVsePlan(VsePlan):

    def __init__(self, owner, scopeId, level, perkId, callback):
        super(ImmediateVsePlan, self).__init__(owner, scopeId, level, perkId)
        self.__onStartCallback = callback

    def _onStartEvent(self, event):
        super(ImmediateVsePlan, self)._onStartEvent(event)
        self.__onStartCallback(self.scopeId, self.perkId)


class PCPlanHolder(object):

    def __init__(self, scopedPerks):
        self._plans = []
        self._scopedPerks = scopedPerks

    def start(self):
        for plan in self._plans:
            plan.start()

    def destroy(self):
        self._clean()

    def loadPlan(self, owner, isAutoStart=False):
        for scopeId in range(len(self._scopedPerks)):
            for perkId, level in self._scopedPerks[scopeId]:
                plan = VsePlan(owner, scopeId, level, perkId)
                plan.loadPlan(isAutoStart)
                self._plans.append(plan)

    def setInputParam(self, paramName, paramValue):
        for plan in self._plans:
            plan.setInputParam(paramName, paramValue)

    def triggerVSPlanEvent(self, event):
        if not self.isPlansReady:
            return
        for plan in self._plans:
            plan.triggerVSPlanEvent(event)

    def reload(self, owner, scopedPerks):
        self._clean()
        self._plans = []
        self._scopedPerks = scopedPerks
        self.loadPlan(owner, True)

    def _clean(self):
        for plan in self._plans:
            plan.destroy()

        del self._plans[:]

    @property
    def isPlansReady(self):
        for value in self._plans:
            if not value.isReady:
                return False

        return True


class RestartingMultiPlan(PCPlanHolder):

    def __init__(self, scopedPerks, callback):
        super(RestartingMultiPlan, self).__init__(scopedPerks)
        self._scheduledPlans = defaultdict(list)
        self._onStartedCallback = callback

    def start(self):
        for plan in self._plans:
            plan.start()

    def loadPlan(self, owner, isAutoStart=False):
        self.__schedulePlans()
        for scopeId in range(len(self._scopedPerks)):
            for perkId, level in self._scopedPerks[scopeId]:
                plan = ImmediateVsePlan(owner, scopeId, level, perkId, self.__onPlanStarted)
                plan.loadPlan(isAutoStart)
                self._plans.append(plan)

    def allPerksDone(self):
        return not self._scheduledPlans

    def reloadPlans(self):
        for plan in self._plans:
            plan.restart()

    def restorePlans(self, ignoredPerks):
        ignored = copy(ignoredPerks)
        for plan in self._plans:
            if plan.perkId in ignored:
                plan.restart()

    def deactivatePerk(self, perkName):
        for plan in self._plans:
            if plan.perkId == perkName:
                plan.triggerVSPlanEvent(PLATOON_VS_PLAN_SIMPLE_EVENT.CLIENT_DEACTIVATION_EVENT)

    def __schedulePlans(self):
        self._scheduledPlans = defaultdict(list)
        for scopeId in range(len(self._scopedPerks)):
            for perkId, _ in self._scopedPerks[scopeId]:
                self._scheduledPlans[scopeId].append(perkId)

    def __onPlanStarted(self, scopeID, perkID):
        if scopeID not in self._scheduledPlans or perkID not in self._scheduledPlans[scopeID]:
            return
        self._scheduledPlans[scopeID].remove(perkID)
        if not self._scheduledPlans[scopeID]:
            self._scheduledPlans.pop(scopeID)
        if self.allPerksDone():
            self._onStartedCallback()
