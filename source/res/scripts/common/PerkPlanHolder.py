# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/PerkPlanHolder.py
from collections import defaultdict
from constants import IS_CELLAPP, IS_BASEAPP
from typing import TYPE_CHECKING, List, Optional
from wg_async import wg_async, wg_await, distributeLoopOverTicks, AsyncEvent
from perks.PerksLoadStrategy import getLoadStarategy, LoadType, LoadState
from perks.vse_plan import VsePlan
if IS_CELLAPP or IS_BASEAPP:
    from server_constants import VEHICLE_STATUS
if TYPE_CHECKING:
    from Vehicle import Vehicle

class PCPlanHolder(object):

    def __init__(self, scopedPerks, owner, loadType):
        self._plans = []
        self._owner = owner
        self._scopedPerks = scopedPerks
        self.isAllPlansLoaded = AsyncEvent(False, None)
        self._isReadyForEvent = AsyncEvent(False, None)
        self._contextEventsScheme = None
        self._delayedEvents = []
        self._loader = getLoadStarategy(loadType)(self._plans, self._scopedPerks, self._owner, self._onPlanReady)
        return

    def start(self):
        if self._loader:
            self._loader.start()

    def beforeBattleStart(self):
        if self._loader:
            self._loader.beforeBattleStart()

    def destroy(self):
        self.clean()
        self._owner = None
        self._scopedPerks = None
        self._contextEventsScheme = None
        self._loader = None
        return

    def setScopedPerks(self, scopedPerks):
        self._scopedPerks = scopedPerks

    def loadPlans(self):
        self._loader.load()

    def loadPlan(self, owner, loadScopeID, loadPerkID, isAutostart=False):
        scope, creator = self._scopedPerks[loadScopeID]
        callback = self._loader._onStatusChanged() if self._loader else self._onPlanReady()
        for perkID, (level, args) in scope:
            if perkID != loadPerkID:
                continue
            plan = VsePlan(owner, loadScopeID, level, loadPerkID, callback, args)
            self.isAllPlansLoaded.clear()
            self._setReady(False)
            plan.load(creator, isAutostart)
            self._plans.append(plan)
            break

    def triggerVSPlanEvent(self, event):
        if not self._isReadyForEvent.is_set():
            if self._loader and self._loader.state in LoadState.STATUS_LOADED:
                self._delayedEvents.append(event)
            return
        if not self._contextEventsScheme:
            return
        if IS_CELLAPP or IS_BASEAPP:
            serverActiveStatuses = (VEHICLE_STATUS.FIGHTING, VEHICLE_STATUS.BEFORE_ARENA)
            if self._owner.status not in serverActiveStatuses:
                return
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

    def reload(self, scopedPerks):
        self._forceClean()
        self._scopedPerks = scopedPerks
        self._loader = getLoadStarategy(LoadType.AUTO_START)(self._plans, self._scopedPerks, self._owner, self._onPlanReady)
        self._loader.load()

    @wg_async
    def clean(self):
        self.isAllPlansLoaded.clear()
        self._setReady(False)

        def asyncLoop():
            for plan in self._plans:
                yield plan.destroy()

        yield wg_await(distributeLoopOverTicks(asyncLoop(), maxPerTick=1, logID='clean'))
        del self._plans[:]

    def unloadPlan(self, perkID):
        for index, plan in enumerate(self._plans):
            if plan.perkId == perkID:
                plan.destroy()
                del self._plans[index]
                break

    def _getContextEventsScheme(self):
        events = defaultdict(list)
        for plan in self._plans:
            for usedEvent in plan.usedEvents:
                events[usedEvent].append(plan)

        return events

    def getPlan(self, scopeID, perkID):
        for plan in self._plans:
            if plan.perkId == perkID and plan.scopeId == scopeID:
                return plan

        return None

    def _setReady(self, ready=True):
        self._isReadyForEvent.clear()
        if ready:
            self._isReadyForEvent.set()
            self._setContextEventsScheme()

    def _forceClean(self):
        self.isAllPlansLoaded.clear()
        self._setReady(False)
        for plan in self._plans:
            plan.destroy()

        del self._plans[:]

    def _setContextEventsScheme(self):
        self._contextEventsScheme = self._getContextEventsScheme()

    def _onPlanReady(self):
        if self._checkIsAllPlansLoaded():
            self.isAllPlansLoaded.set()
        if self._checkIsAllPlansReady():
            self._setReady()
            self._loader = None
            self._sendDelayedEvents()
        return

    def _sendDelayedEvents(self):
        for event in self._delayedEvents:
            self.triggerVSPlanEvent(event)

        del self._delayedEvents[:]

    def _checkIsAllPlansReady(self):
        return all((plan.isPlanStarted for plan in self._plans))

    def _checkIsAllPlansLoaded(self):
        return all((plan.isPlanLoaded for plan in self._plans))
