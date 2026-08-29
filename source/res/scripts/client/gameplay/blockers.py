# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/blockers.py
import logging
import weakref
from itertools import chain
import typing
from wg_async import wg_async, AsyncEvent
from frameworks_common.state_machine import StringEventTransition, State, StateFlags
if typing.TYPE_CHECKING:
    from frameworks_common.state_machine import StringEvent
_logger = logging.getLogger(__name__)

class BlockingStateMixin(object):

    class _Blocker(object):

        def __init__(self, eventToBlockOn):
            self.event = AsyncEvent()
            self._weakEvent = weakref.ref(eventToBlockOn, self.clear)
            eventToBlockOn += self.event.set

        def clear(self, *_, **__):
            event = self._weakEvent()
            if event:
                event -= self.event.set
            self.event.destroy()
            self.event = None
            return

    def __init__(self):
        self._enterBlockers = []
        self._exitBlockers = []
        self._blockerClearLifetimeStateID = None
        return

    @property
    def blockerClearLifetimeStateID(self):
        return self._blockerClearLifetimeStateID

    def clearBlockers(self):
        for blocker in chain(self._enterBlockers, self._exitBlockers):
            blocker.clear()

        self._enterBlockers = []
        self._exitBlockers = []

    def addEnterBlocker(self, event):
        self._enterBlockers.append(self._Blocker(event))

    def addExitBlocker(self, event):
        self._exitBlockers.append(self._Blocker(event))

    def enterBlockersSatisfied(self):
        return not self._enterBlockers or all((blocker.event.is_set() for blocker in self._enterBlockers))

    def exitBlockersSatisfied(self):
        return not self._exitBlockers or all((blocker.event.is_set() for blocker in self._exitBlockers))

    @wg_async
    def waitEnterBlockersSatisfied(self):
        for enterBlocker in self._enterBlockers:
            yield enterBlocker.event.wait()

    @wg_async
    def waitExitBlockersSatisfied(self):
        for exitBlocker in self._exitBlockers:
            yield exitBlocker.event.wait()


class BlockingState(State, BlockingStateMixin):

    def __init__(self, stateID, blockerClearLifetimeStateID, flags=StateFlags.UNDEFINED):
        State.__init__(self, stateID=stateID, flags=flags)
        BlockingStateMixin.__init__(self)
        self._blockerClearLifetimeStateID = blockerClearLifetimeStateID

    def clear(self):
        self.clearBlockers()
        super(BlockingState, self).clear()


class BlockableTransition(StringEventTransition):

    def __init__(self, token, priority=0):
        super(BlockableTransition, self).__init__(token=token, priority=priority)
        self._repostFuture = None
        return

    def clear(self):
        if self._repostFuture is not None:
            self._repostFuture.cancel()
            self._repostFuture = None
        return

    def execute(self, event):
        stringEventMatches = super(BlockableTransition, self).execute(event)
        if not stringEventMatches:
            return False
        if self._sourceAndTargetSatisfied():
            return True
        if self._repostFuture:
            self._repostFuture.cancel()
        self._repostFuture = self._repostWhenUnblocked(event)
        return False

    def _sourceAndTargetSatisfied(self):
        source = self.getSource()
        sourceSatisfied = not isinstance(source, BlockingStateMixin) or source.exitBlockersSatisfied()
        targetsSatisfied = all((not isinstance(target, BlockingStateMixin) or target.enterBlockersSatisfied() for target in self.getTargets()))
        return source.isEntered() and sourceSatisfied and targetsSatisfied

    @wg_async
    def _repostWhenUnblocked(self, event):
        source = self.getSource()
        _logger.debug('Waiting for blockers for %r', source)
        hadBlocks = True
        while hadBlocks:
            hadBlocks = False
            if isinstance(source, BlockingStateMixin):
                if not source.exitBlockersSatisfied():
                    _logger.debug('Waiting for exit blockers on %r:', source)
                    hadBlocks = True
                yield source.waitExitBlockersSatisfied()
            for target in self.getTargets():
                if isinstance(target, BlockingStateMixin):
                    if not target.enterBlockersSatisfied():
                        _logger.debug('Waiting for enter blockers on %r:', target)
                        hadBlocks = True
                    yield target.waitEnterBlockersSatisfied()

        if source.isEntered():
            _logger.info('Reposting %r from %r.', event, self)
            source.getMachine().post(event)
        else:
            _logger.info('Not reposting %r, because %r is no longer entered.', event, source)
