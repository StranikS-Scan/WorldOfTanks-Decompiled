# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/perks/vse_plan.py
import BigWorld
import VSE
from constants import IS_CELLAPP
from items import perks
from visual_script.misc import ASPECT
from functools import wraps
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV, LOG_WARNING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from visual_script.contexts.perks_context import PerkContext

def callOnValidState(f):

    @wraps(f)
    def w(self, *args, **kwargs):
        if getattr(self, '_plan') is None:
            LOG_DEBUG_DEV('VsePlan.{} called when plan is None'.format(f.__name__))
            return
        else:
            return f(self, *args, **kwargs)

    return w


class PlanStatus:
    DEFAULT = 0
    LOAD = 1
    START = 2
    DESTROYED = 3


class VsePlan(object):
    _PLAN_PATH = 'vscript/plans/{}.xml'
    _PLAN_ID_PREFIX = 'abilityPerks/perk_'

    def __init__(self, owner, scopeId, level, perkId, onReadyCallback, contextArgs):
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
        self.__callback = onReadyCallback
        self._contextArgs = contextArgs
        self._isPlanStarted = False
        self._status = PlanStatus.DEFAULT
        return

    @property
    def hasContext(self):
        return self._context is not None

    @property
    def usedEvents(self):
        return self._usedEvents

    @property
    def isPlanLoaded(self):
        return self._isPlanLoaded

    @property
    def isPlanStarted(self):
        return self._isPlanStarted

    @property
    def status(self):
        return self._status

    def load(self, contextCreator, isAutoStart=False):
        self._contextCreator = contextCreator
        self._isAutoStart = isAutoStart
        self._isPlanLoaded = False
        self._plan = VSE.Plan()
        if not perks.g_cache.perks.validatePerk(self.perkId):
            LOG_ERROR("Perk '%s' not found" % self.perkId)
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
            self._isPlanStarted = True
            self.__setStatus(PlanStatus.START)
        else:
            LOG_ERROR("VsePlan: Plan '%s' not created before start" % self._planId)
        return

    def stop(self):
        self._plan.stop()

    @callOnValidState
    def triggerVSPlanEvent(self, event):
        context = self._context
        if context is None:
            LOG_ERROR('VsePlan: context not ready or not set! Event: %s' % event)
            return
        else:
            if isinstance(event, str):
                context.triggerEvent(event)
            elif isinstance(event, tuple) and hasattr(event, '_fields'):
                context.triggerEvent(event.__class__.__name__, *(value for value in event))
            return

    def destroy(self):
        if self._plan is not None:
            self._plan.stop()
        else:
            ownerId = self._owner.id if self._owner else -1
            LOG_WARNING('[PerksController] No plan for perkID:{0} vehicleID:{1} after destroy in applySelectedSetup '.format(self.perkId, ownerId))
        self._plan = None
        self._isPlanLoaded = False
        self._isAutoStart = False
        self._owner = None
        self._context = None
        self._contextCreator = None
        self._status = PlanStatus.DESTROYED
        self._clearCallBack()
        return

    def setContextArgs(self, contextArgs):
        self._contextArgs = contextArgs
        self._context = context = self._contextCreator(self.perkId, self._level, self.scopeId, *self._contextArgs)
        self._plan.setContext(context)

    def _onPlanPreLoaded(self, future=None):
        try:
            if IS_CELLAPP:
                future.get()
            if self.status == PlanStatus.DESTROYED:
                LOG_ERROR("VsePlan: Plan xml '%s' already destroyed." % self._planId)
                return
            self._usedEvents = []
            self._isPlanLoaded = self._plan.load(self._planId, (ASPECT.SERVER, ASPECT.CLIENT), [], self._usedEvents)
            if self._isPlanLoaded and self._contextCreator:
                self._context = context = self._contextCreator(self.perkId, self._level, self.scopeId, *self._contextArgs)
                self._plan.setContext(context)
                self.__setStatus(PlanStatus.LOAD)
            if self._isAutoStart:
                self.start()
        except BigWorld.FutureNotReady:
            LOG_ERROR("VsePlan: Plan xml '%s' not pre-loaded." % self._planId)

    def _clearCallBack(self):
        self.__callback = None
        return

    def __setStatus(self, value):
        self._status = value
        if self.__callback:
            self.__callback()
