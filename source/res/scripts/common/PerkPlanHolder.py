# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/PerkPlanHolder.py
from functools import wraps
from collections import defaultdict
import BigWorld
import VSE
from typing import Callable, Optional
from copy import copy
from itertools import izip
from VSPlanEvents import PERK_EVENTS
from constants import IS_CELLAPP
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV
from items import perks
from visual_script.misc import ASPECT

def callOnValidState(f):

    @wraps(f)
    def w(self, *args, **kwargs):
        if getattr(self, '_plan') is None:
            LOG_DEBUG_DEV('VsePlan.{} called when plan is None'.format(f.__name__))
            return
        else:
            return f(self, *args, **kwargs)

    return w


class VsePlan(object):
    _PLAN_PATH = 'vscript/plans/{}.xml'
    _PLAN_ID_PREFIX = 'abilityPerks/perk_'

    def __init__(self, owner, scopeId, level, perkId):
        self._owner = owner
        self.scopeId = scopeId
        self.perkId = perkId
        self._level = level
        self._planId = self._PLAN_ID_PREFIX + str(self.perkId)
        self._isPlanLoaded = False
        self._isAutoStart = False
        self._plan = None
        self._context = None
        self._contextCreator = None
        self._usedEvents = []
        return

    @property
    def hasContext(self):
        return self._context is not None

    @property
    def usedEvents(self):
        return self._usedEvents

    def loadPlan(self, contextCreator, isAutoStart=False):
        self._contextCreator = contextCreator
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

    @callOnValidState
    def setInputParam(self, paramName, paramValue):
        self._plan.setOptionalInputParam(paramName, paramValue)

    def start(self):
        if self._plan is not None:
            if not self._isPlanLoaded:
                self._isAutoStart = True
                return
            self._plan.start()
        else:
            LOG_ERROR("VsePlan: Plan '%s' not created before start" % self._planId)
        return

    @callOnValidState
    def restart(self, restore=False):
        if restore:
            self._context.setPerkLevel(self._level)
        self._sendEventByContext(PERK_EVENTS.PERK_RESTARTED)

    @callOnValidState
    def subLevel(self, level):
        self._context.setPerkLevel(self._context.perkLevel - level)
        self.restart()

    @callOnValidState
    def triggerVSPlanEvent(self, event):
        self._sendEventByContext(event)
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
        self._isAutoStart = False
        return

    def _onPlanPreLoaded(self, future=None):
        try:
            if IS_CELLAPP:
                future.get()
            self._usedEvents = []
            self._isPlanLoaded = self._plan.load(self._planId, (ASPECT.SERVER, ASPECT.CLIENT), [], self._usedEvents)
            if self._isPlanLoaded and self._contextCreator:
                self._context = context = self._contextCreator(self.perkId, self._level, self.scopeId)
                self._plan.setContext(context)
            if self._isAutoStart:
                self.start()
        except BigWorld.FutureNotReady:
            LOG_ERROR("VsePlan: Plan xml '%s' not pre-loaded." % self._planId)

    def _onStartEvent(self, event):
        self.triggerVSPlanEvent(event)

    def _sendEventByContext(self, event, *args):
        if not self.hasContext:
            LOG_ERROR('VsePlan: context not ready or not set! Event: %s' % event)
            return
        LOG_DEBUG_DEV('VsePlan: _sendEventByContext: ', event, *args)
        context = self._context
        if isinstance(event, str):
            context.triggerEvent(event, *args)
        elif isinstance(event, tuple) and hasattr(event, '_fields'):
            context.triggerEvent(event.__class__.__name__, *(value for value in event))


class PCPlanHolder(object):

    def __init__(self, scopedPerks):
        self._plans = []
        self._scopedPerks = scopedPerks
        self._isReady = False
        self._contextCreator = None
        self._contextEventsScheme = None
        return

    def start(self):
        for plan in self._plans:
            plan.start()

    def destroy(self):
        self.clean()
        self._scopedPerks = None
        self._contextEventsScheme = None
        return

    def loadPlan(self, contextCreator, owner, isAutoStart=False):
        self._contextCreator = contextCreator
        for scopeId, scope in self._scopedPerks.iteritems():
            for perkId, level in scope:
                plan = VsePlan(owner, scopeId, level, perkId)
                plan.loadPlan(contextCreator, isAutoStart)
                self._plans.append(plan)

    def setInputParam(self, paramName, paramValue):
        for plan in self._plans:
            plan.setInputParam(paramName, paramValue)

    def triggerVSPlanEvent(self, event):
        if not self._isReady:
            return
        elif not self._contextEventsScheme:
            return
        else:
            eventName = None
            if isinstance(event, str):
                eventName = event
            elif isinstance(event, tuple) and hasattr(event, '_fields'):
                eventName = event.__class__.__name__
            else:
                return
            plans = []
            if eventName in self._contextEventsScheme:
                plans = self._contextEventsScheme[eventName]
            for plan in plans:
                plan.triggerVSPlanEvent(event)

            return

    def reload(self, owner, scopedPerks):
        self.clean()
        self._scopedPerks = scopedPerks
        self.loadPlan(self._contextCreator, owner, True)

    def clean(self):
        for plan in self._plans:
            plan.destroy()

        del self._plans[:]

    def setReady(self, ready=True):
        self._isReady = ready
        if ready:
            self._contextEventsScheme = self.getContextEventsScheme()

    def getContextEventsScheme(self):
        events = defaultdict(list)
        for plan in self._plans:
            for usedEvent in plan.usedEvents:
                events[usedEvent].append(plan)

        return events


class RestartingMultiPlan(PCPlanHolder):

    def __init__(self, scopedPerks):
        super(RestartingMultiPlan, self).__init__(scopedPerks)
        self._inProcess = False

    def start(self):
        for plan in self._plans:
            plan.start()

    def reloadPlans(self):
        self._inProcess = True
        for plan in self._plans:
            plan.restart()

        self._inProcess = False

    def restorePlans(self, ignoredPerks):
        ignored = copy(ignoredPerks)
        for plan in self._plans:
            if plan.scopeId in ignored and plan.perkId in ignored[plan.scopeId]:
                plan.restart(restore=True)

    def recalcPerks(self, scope, perks):
        for plan in self._plans:
            if plan.scopeId == scope and plan.perkId in perks:
                plan.subLevel(perks[plan.perkId])

    @property
    def inProcess(self):
        return self._inProcess
