# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints/queues.py
import time
from functools import partial
import typing
from typing import Optional, Dict, Union, Tuple, List, Type
import BigWorld
import SoundGroups
from gui.battle_control.controllers.battle_hints.common import getLogger, DEFAULT_LOGGER_NAME, HIGHEST_PRIORITY, QUEUE_HINTS_MAX_SIZE, HIDE_ANIMATION_TIMEOUT
from shared_utils import safeCancelCallback
from helpers.log.adapters import getWithContext
from wotdecorators import condition
from debug_utils import LOG_WARNING
from PlayerEvents import g_playerEvents
if typing.TYPE_CHECKING:
    import weakref
    from hints.battle.schemas.base import CHMType
    from gui.battle_control.controllers.battle_hints.component import BattleHintComponent
    from gui.battle_control.controllers.battle_hints.history import BattleHintsHistory
_hintLogger = getLogger('Queue', 'Hint')
_mgrLogger = getLogger('Queues', 'Mgr')

class BattleHint(object):
    __slots__ = ('_model', '_component', '_history', '_params', '_enqueueTime', '_startDisplayTime', '_maxPriorityOffset')

    def __init__(self, model, component, history=None, params=None):
        self._model = model
        self._component = component
        self._history = history
        self._params = params or {}
        self._enqueueTime = 0
        self._startDisplayTime = 0
        self._maxPriorityOffset = -1

    @property
    def model(self):
        return self._model

    @property
    def uniqueName(self):
        return self._model.uniqueName

    @property
    def unique(self):
        return self._model.props.unique

    @property
    def showTime(self):
        return self._model.lifecycle.showTime

    @property
    def minShowTime(self):
        return self._model.lifecycle.minShowTime

    @property
    def minDisplayTimeLeft(self):
        displayTime = max(time.time() - self._startDisplayTime, 0) if self._startDisplayTime > 0 else 0
        return max(self.minShowTime - displayTime, 0)

    @property
    def params(self):
        return self._params

    def setMaxPriority(self, offset):
        self._maxPriorityOffset = offset
        _hintLogger.debug('<%s> set to max priority offset <%s>.', self.uniqueName, self._maxPriorityOffset)

    def getPriority(self, currentTime):
        if self._maxPriorityOffset >= 0:
            return (HIGHEST_PRIORITY + self._maxPriorityOffset, HIGHEST_PRIORITY)
        lastDisplayTime = 0.0
        if self._model.history and self.model.history.modifyPriority:
            lastDisplayTime = self._getLastDisplayTime()
        return (self._model.props.priority, currentTime - lastDisplayTime)

    def canBeShown(self, currentTime=None):
        return self._model.canBeShown(self._history) and not self._isOnCooldown(currentTime)

    def enqueued(self):
        self._enqueueTime = time.time()
        _hintLogger.debug('<%s> enqueued.', self.uniqueName)

    def show(self):
        self._enqueueTime = 0
        self._startDisplayTime = time.time()
        self._playSound()
        try:
            self._component.showHint(self._model, self._params)
            _hintLogger.debug('<%s> shown.', self.uniqueName)
        except ReferenceError:
            _hintLogger.debug('Component already destroyed and cannot be shown.')

    def hide(self):
        self._startDisplayTime = 0
        try:
            self._component.hideHint()
            _hintLogger.debug('<%s> hidden.', self.uniqueName)
        except ReferenceError:
            _hintLogger.debug('Component already destroyed and cannot be hidden.')

    def cancelFadeOut(self):
        try:
            self._component.cancelFadeOut()
            _hintLogger.debug('<%s> fade out cancelled.', self.uniqueName)
        except ReferenceError:
            _hintLogger.debug('Component already destroyed, fadeout cannot be canceled.')

    def isOutdated(self, currentTime):
        if not self.canBeShown(currentTime):
            return True
        return False if self._enqueueTime <= 0 or self._model.lifecycle.waitTime <= 0 else currentTime - self._enqueueTime >= self._model.lifecycle.waitTime

    def _getLastDisplayTime(self):
        return 0.0 if not self._model.history or not self._history else self._history.getLastDisplayTime(self._model.uniqueName)

    def _isOnCooldown(self, currentTime=None):
        if not self._model.history or self._model.history.cooldown <= 0:
            return False
        currentTime = currentTime or time.time()
        return self._model.history.cooldown >= currentTime - self._getLastDisplayTime()

    def _playSound(self):
        if not self._model.sound:
            return
        else:
            soundFx = self._model.sound.createFx()
            if soundFx:
                SoundGroups.g_instance.playSound2D(soundFx)
                _hintLogger.debug('<%s> fx sound <%s> played.', self.uniqueName, soundFx)
            soundNotify = self._model.sound.createNotify()
            if soundNotify:
                soundNotifications = getattr(BigWorld.player(), 'soundNotifications', None)
                if soundNotifications is not None:
                    soundNotifications.play(soundNotify)
                    _hintLogger.debug('<%s> notify sound <%s> played.', self.uniqueName, soundNotify)
            return

    def __eq__(self, other):
        return False if not isinstance(other, BattleHint) else self.uniqueName == other.uniqueName

    def __ne__(self, other):
        return not self.__eq__(other)


class BattleHintsQueue(object):
    __slots__ = ('_displayed', '_queue', '_delayerId', '_fadeOutCallbackId', '_enabled', '_maxSize', '_withFadeOut', '_logger')
    ifEnabled = condition('_enabled', logFunc=LOG_WARNING, logStack=False)

    def __init__(self, maxSize=QUEUE_HINTS_MAX_SIZE, withFadeOut=True):
        self._maxSize = maxSize
        self._displayed = None
        self._queue = []
        self._delayerId = None
        self._withFadeOut = withFadeOut
        self._fadeOutCallbackId = None
        self._enabled = True
        self._logger = getWithContext(DEFAULT_LOGGER_NAME, self)
        self._logger.debug('Initialized.')
        return

    @ifEnabled
    def add(self, hint):
        if len(self._queue) >= self._maxSize:
            self._logger.error('Max hints limit <%s> reached.', self._maxSize)
            return
        if hint.unique and (self._displayed and hint == self._displayed or hint in self._queue):
            self._logger.debug('Unique hint <%s> already in queue or displayed.', hint.uniqueName)
            return
        hint.enqueued()
        self._queue.append(hint)
        self._logger.debug('Hint <%s> added to queue.', hint.uniqueName)
        if self._displayed:
            currentTime = time.time()
            if hint.getPriority(currentTime) > self._displayed.getPriority(currentTime):
                showTimeLeft = self._displayed.minDisplayTimeLeft
                if showTimeLeft <= 0:
                    self._showNextHint()
                else:
                    self._restartDelayer(showTimeLeft)
        else:
            self._showNextHint()

    @ifEnabled
    def remove(self, hint):
        self._queue = [ _hint for _hint in self._queue if _hint != hint ]
        self._logger.debug('Hint <%s> removed.', hint.uniqueName)

    @ifEnabled
    def hide(self, hint, immediately=False):
        if self._displayed and self._displayed == hint:
            showTimeLeft = self._displayed.minDisplayTimeLeft
            if immediately or showTimeLeft <= 0:
                self._showNextHint()
            else:
                self._restartDelayer(showTimeLeft)
        else:
            self._logger.debug('Hint <%s> not displayed already.', hint.uniqueName)

    @ifEnabled
    def onFadeOutFinished(self):
        if not self._waitingForFadeOut:
            self._logger.debug('Not waiting for fade out.')
            return
        self._logger.debug('Fade out finished.')
        self._stopWaitingFadeOut()
        self._showNextHint()

    def destroy(self):
        self._enabled = False
        self._queue = []
        self._stopWaitingFadeOut()
        self._stopDelayer()
        self._hide(withFadeOut=False)
        self._logger.debug('Destroyed.')

    @ifEnabled
    def _onWaitingFadeOutTimeout(self, hint):
        self._logger.debug('Fade out waiting timeout.')
        hint.cancelFadeOut()
        self.onFadeOutFinished()

    @property
    def _waitingForFadeOut(self):
        return self._fadeOutCallbackId is not None

    def _showNextHint(self):
        if self._waitingForFadeOut:
            self._logger.debug('Can not show next hint. Waiting for fade out.')
            return
        self._stopDelayer()
        if not self._hide():
            self._logger.debug('Can not select next hint. Hiding display hint in process.')
            return
        self._logger.debug('Selecting next hint.')
        hint = self._selectNextHint()
        if hint:
            self._show(hint)

    def _selectNextHint(self):
        currentTime = time.time()
        self._queue = [ _hint for _hint in self._queue if not _hint.isOutdated(currentTime) ]
        if not self._queue:
            self._logger.debug('Nothing to show from queue.')
            g_playerEvents.onEmptyBattleHintsQueue()
            return None
        else:
            hint = max(self._queue, key=lambda _hint: _hint.getPriority(currentTime))
            self._queue.remove(hint)
            self._logger.debug('Next hint <%s> selected.', hint.uniqueName)
            return hint

    def _show(self, hint):
        self._displayed = hint
        self._displayed.show()
        self._logger.debug('Show hint <%s> for <%s> sec.', hint.uniqueName, hint.showTime)
        self._restartDelayer(hint.showTime)
        g_playerEvents.onShowBattleHint(self._displayed)

    def _hide(self, withFadeOut=True):
        if self._displayed is not None:
            if self._waitingForFadeOut:
                self._logger.error('Hide|show flow broken. Fade out not finished.')
                self._stopWaitingFadeOut()
            if withFadeOut and self._withFadeOut:
                self._startWaitingFadeOut(self._displayed)
            displayed = self._displayed
            g_playerEvents.onHideBattleHint(self._displayed)
            self._displayed = None
            self._logger.debug('Hide hint <%s>.', displayed.uniqueName)
            displayed.hide()
        return not self._waitingForFadeOut

    def _stopWaitingFadeOut(self):
        if self._fadeOutCallbackId is not None:
            safeCancelCallback(self._fadeOutCallbackId)
            self._fadeOutCallbackId = None
            self._logger.debug('Stop waiting fade out.')
        return

    def _startWaitingFadeOut(self, hint):
        if self._fadeOutCallbackId is None:
            self._fadeOutCallbackId = BigWorld.callback(HIDE_ANIMATION_TIMEOUT, partial(self._onWaitingFadeOutTimeout, hint))
            self._logger.debug('Start waiting fade out.')
        return

    def _stopDelayer(self):
        if self._delayerId is not None:
            safeCancelCallback(self._delayerId)
            self._delayerId = None
            self._logger.debug('Stop delayer.')
        return

    def _restartDelayer(self, delay):
        self._stopDelayer()
        if self._delayerId is None and delay > 0:
            self._delayerId = BigWorld.callback(delay, self._showNextHint)
            self._logger.debug('Start delayer with <%s> delay.', delay)
        return


class BattleHintQueueParams(object):
    __slots__ = ('_name', '_queueClass', '_hintClass', '_queueId', '_maxSize', '_withFadeOut')

    def __init__(self, name, queueClass=None, maxSize=QUEUE_HINTS_MAX_SIZE, withFadeOut=True, hintClass=None):
        self._name = name
        self._queueClass = queueClass or BattleHintsQueue
        self._maxSize = maxSize
        self._withFadeOut = withFadeOut
        self._hintClass = hintClass or BattleHint
        self._queueId = hash((self._name,
         id(self._queueClass),
         self._maxSize,
         self._withFadeOut))

    @property
    def queueId(self):
        return self._queueId

    def createQueue(self):
        return self._queueClass(maxSize=self._maxSize, withFadeOut=self._withFadeOut)

    def createHint(self, model, component, history=None, params=None):
        return self._hintClass(model=model, component=component, history=history, params=params)

    def __repr__(self):
        return 'BHQueueParams<{}, {}>'.format(self._name, self._queueId)


class BattleHintsQueuesMgr(object):
    __slots__ = ('_queues', '_enabled')
    ifEnabled = condition('_enabled', logFunc=LOG_WARNING, logStack=False)

    def __init__(self):
        self._queues = {}
        self._enabled = True
        _mgrLogger.debug('Initialized.')

    @ifEnabled
    def get(self, params):
        if params.queueId not in self._queues:
            self._queues[params.queueId] = params.createQueue()
            _mgrLogger.debug('Queue [%s] created.', params.queueId)
        return self._queues[params.queueId]

    def destroy(self):
        self._enabled = False
        for queue in self._queues.itervalues():
            queue.destroy()

        self._queues.clear()
        _mgrLogger.debug('Destroyed.')
