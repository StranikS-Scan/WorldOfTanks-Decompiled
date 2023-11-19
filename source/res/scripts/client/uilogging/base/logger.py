# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/base/logger.py
import uuid
import typing
import logging
from functools import wraps
import BigWorld
from helpers import dependency
from skeletons.ui_logging import IUILoggingCore
from uilogging.constants import LogLevels, DEFAULT_LOGGER_NAME
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from uilogging.types import FeatureType, GroupType, ActionType, LogLevelType, PartnerIdType, TimeLimitType, ItemType, ItemStateType, ParentScreenType, InfoType, SourceItemType, DestinationItemType, TransitionMethodType
_logger = logging.getLogger(DEFAULT_LOGGER_NAME)

def createPartnerID():
    return str(uuid.uuid4())


def ifUILoggingEnabled(result=None):

    def inner(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.disabled:
                _logger.debug('UI logging disabled. %s log call skipped.', self)
                return result
            return func(self, *args, **kwargs)

        return wrapper

    return inner


class _BaseLogger(object):
    __slots__ = ('_feature', '_group', '_logOnceSet', '_timedActions', '_suspendedActions')
    _core = dependency.descriptor(IUILoggingCore)

    def __init__(self, feature, group):
        self._feature = feature
        self._group = group
        self._logOnceSet = set()
        self._timedActions = {}
        self._suspendedActions = {}

    def __str__(self):
        return '<{}: {}, {}>'.format(self.__class__.__name__, self._feature, self._group)

    @noexcept
    def ensureSession(self):
        self._core.ensureSession()

    @noexcept
    def reset(self):
        self._logOnceSet.clear()
        self._timedActions.clear()
        self._suspendedActions.clear()

    @property
    def disabled(self):
        return not self._core.isFeatureEnabled(self._feature)

    @noexcept
    def suspendAction(self, action):
        if action not in self._timedActions:
            return
        if action in self._suspendedActions:
            return
        self._suspendedActions[action] = BigWorld.time()

    @noexcept
    def resumeAction(self, action):
        if action not in self._timedActions:
            return
        else:
            suspensionStartTime = self._suspendedActions.pop(action, None)
            if suspensionStartTime is None:
                return
            suspensionTime = BigWorld.time() - suspensionStartTime
            self._timedActions[action] += suspensionTime
            return

    @noexcept
    @ifUILoggingEnabled()
    def startAction(self, action):
        if action in self._timedActions:
            _logger.debug('%s action: %s already started. Setting new action.', self, action)
        self._timedActions[action] = BigWorld.time()

    @noexcept
    @ifUILoggingEnabled()
    def _log(self, action, loglevel=LogLevels.INFO, **params):
        return self._core.log(feature=self._feature, group=self._group, action=action, loglevel=loglevel, **params)

    @noexcept
    @ifUILoggingEnabled()
    def _logImmediately(self, action, loglevel=LogLevels.INFO, **params):
        return self._core.logImmediately(feature=self._feature, group=self._group, action=action, loglevel=loglevel, **params)

    @noexcept
    @ifUILoggingEnabled()
    def _logOnce(self, action, loglevel=LogLevels.INFO, **params):
        if action in self._logOnceSet:
            _logger.debug('%s log once action: %s already logged.', self, action)
            return
        self._logOnceSet.add(action)
        self._log(action, loglevel=loglevel, **params)

    @noexcept
    def _stopAction(self, action, loglevel=LogLevels.INFO, timeLimit=0.0, **params):
        if action not in self._timedActions:
            _logger.debug('%s action: %s not started.', self, action)
            return
        else:
            if action in self._suspendedActions:
                self.resumeAction(action)
            startTime = self._timedActions.pop(action, None)
            timeSpent = BigWorld.time() - startTime
            if timeSpent > timeLimit:
                self._log(action, loglevel=loglevel, timeSpent=timeSpent, **params)
            return


class MetricsLogger(_BaseLogger):
    __slots__ = ()

    def __init__(self, feature):
        super(MetricsLogger, self).__init__(feature, group='metrics')

    def log(self, action, item, parentScreen=None, itemState=None, info=None, partnerID=None, loglevel=LogLevels.INFO):
        self._log(action, loglevel=loglevel, item=item, parent_screen=parentScreen, item_state=itemState, additional_info=info, partnerID=partnerID)

    def logOnce(self, action, item, parentScreen=None, itemState=None, info=None, partnerID=None, loglevel=LogLevels.INFO):
        self._logOnce(action, loglevel=loglevel, item=item, parent_screen=parentScreen, item_state=itemState, additional_info=info, partnerID=partnerID)

    def stopAction(self, action, item, parentScreen=None, itemState=None, info=None, partnerID=None, loglevel=LogLevels.INFO, timeLimit=0.0):
        self._stopAction(action, loglevel=loglevel, timeLimit=timeLimit, item=item, parent_screen=parentScreen, item_state=itemState, additional_info=info, partnerID=partnerID)


class FlowLogger(_BaseLogger):
    __slots__ = ()

    def __init__(self, feature):
        super(FlowLogger, self).__init__(feature, group='flow')

    def log(self, action, sourceItem, destinationItem, transitionMethod, partnerID=None, loglevel=LogLevels.INFO):
        self._log(action, loglevel=loglevel, source_item=sourceItem, destination_item=destinationItem, transition_method=transitionMethod, partnerID=partnerID)

    def logOnce(self, action, sourceItem, destinationItem, transitionMethod, partnerID=None, loglevel=LogLevels.INFO):
        self._logOnce(action, loglevel=loglevel, source_item=sourceItem, destination_item=destinationItem, transition_method=transitionMethod, partnerID=partnerID)

    def stopAction(self, action, sourceItem, destinationItem, transitionMethod, partnerID=None, loglevel=LogLevels.INFO, timeLimit=0.0):
        self._stopAction(action, loglevel=loglevel, timeLimit=timeLimit, source_item=sourceItem, destination_item=destinationItem, transition_method=transitionMethod, partnerID=partnerID)


LOGGERS_TYPING = typing.Union[FlowLogger, MetricsLogger]
