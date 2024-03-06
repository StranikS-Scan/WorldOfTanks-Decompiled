# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints/controller.py
import sys
import weakref
import typing
from typing import Optional, Dict, Tuple
import BattleReplay
import replay
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.battle_hints.common import getLogger
from gui.battle_control.controllers.battle_hints.queues import BattleHintsQueuesMgr
from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
from gui.battle_control.controllers.battle_hints.history import BattleHintsHistory
from hints.battle import manager as battleHintsModelsMgr
from shared_utils import findFirst
from ids_generators import SequenceIDGenerator
from wotdecorators import condition
if typing.TYPE_CHECKING:
    from hints.battle.schemas.base import CHMType
    from gui.battle_control.controllers.battle_hints.queues import BattleHintsQueue, BattleHint
_logger = getLogger('Controller')

class BattleHintsController(ViewComponentsController):
    __slots__ = ('_modelsMgr', '_queuesMgr', '_history', '_maxPriorityOffset', '_components', '__weakref__', '_replayController', '_closeOnRoundFinished', '_started')
    ifStarted = condition('_started', logFunc=LOG_DEBUG, logStack=False)

    def __init__(self, closeOnRoundFinished=True):
        super(BattleHintsController, self).__init__()
        self._closeOnRoundFinished = closeOnRoundFinished
        self._started = False
        self._modelsMgr = battleHintsModelsMgr.get()
        self._queuesMgr = BattleHintsQueuesMgr()
        self._history = BattleHintsHistory()
        self._maxPriorityOffset = SequenceIDGenerator(lowBound=0, highBound=sys.maxint)
        self._components = {}
        self._replayController = None
        _logger.debug('Initialized.')
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_HINTS

    def startControl(self, *args):
        self._started = True
        self._replayController = replay.getReplayController(weakref.proxy(self))
        if self._closeOnRoundFinished:
            g_playerEvents.onRoundFinished += self._onRoundFinished
        _logger.debug('Started.')

    def stopControl(self):
        self._stop()
        if self._replayController is not None:
            self._replayController.fini()
            self._replayController = None
        _logger.debug('Stopped.')
        return

    @ifStarted
    def showHint(self, hintName, params=None, immediately=False):
        hint, queue = self._prepare(hintName, params=params)
        if hint and queue and hint.canBeShown():
            if immediately:
                hint.setMaxPriority(self._maxPriorityOffset.next())
            queue.add(hint)

    @ifStarted
    def hideHint(self, hintName):
        hint, queue = self._prepare(hintName)
        if hint and queue:
            queue.hide(hint)

    @ifStarted
    def removeHint(self, hintName, hide=False):
        hint, queue = self._prepare(hintName)
        if hint and queue:
            queue.remove(hint)
            if hide:
                queue.hide(hint)

    @ifStarted
    def onFadeOutFinished(self, component):
        queue = self._queuesMgr.get(component.getBattleHintsQueueParams())
        if queue:
            queue.onFadeOutFinished()

    def getComponent(self, alias):
        if alias in self._components:
            component = self._components[alias]
            _logger.debug('Getting component <%s> by alias <%s> from cache.', component, alias)
        else:
            component = self._findComponent(alias)
            if component is None:
                _logger.debug('Can not find component by alias <%s>.', alias)
                return
            if not isinstance(component, BattleHintComponent):
                _logger.error('Unsupported component <%s> type.', alias)
                component = None
            self._components[alias] = component
            _logger.debug('Adding component %s by alias <%s> to cache.', component, alias)
        return component

    def _onRoundFinished(self, *_, **__):
        self._stop()

    def _stop(self):
        self._started = False
        self._modelsMgr = None
        self._queuesMgr.destroy()
        self._history.destroy()
        self._components.clear()
        self._maxPriorityOffset.clear()
        if self._closeOnRoundFinished:
            g_playerEvents.onRoundFinished -= self._onRoundFinished
        _logger.debug('Cleared.')
        return

    def _prepare(self, hintName, params=None):
        if BattleReplay.isPlaying():
            _logger.debug('Hints are not showed by controller during the replay.')
            return (None, None)
        else:
            model = self._getModel(hintName)
            if not model:
                return (None, None)
            alias = model.props.component
            component = self.getComponent(alias)
            if not component:
                return (None, None)
            queueParams = component.getBattleHintsQueueParams()
            return (queueParams.createHint(model, component, self._history, params), self._queuesMgr.get(queueParams))

    def _getModel(self, hintName):
        if not self._modelsMgr:
            _logger.warning('Models manager not initialized.')
            return None
        model = self._modelsMgr.get(hintName)
        if not model:
            _logger.error('Unknown hint <%s>.', hintName)
            return None
        elif not model.validate():
            _logger.debug('Not suitable hint <%s> or hint is disabled.', hintName)
            return None
        else:
            return model

    def _findComponent(self, alias):
        return findFirst(lambda comp: comp.getAlias() == alias, self._viewComponents, default=None)
