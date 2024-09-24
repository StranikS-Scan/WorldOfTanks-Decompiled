# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints/history.py
import time
import typing
import BattleReplay
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from debug_utils import LOG_WARNING
from gui.battle_control.controllers.battle_hints.common import getLogger
from wotdecorators import condition
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.battle_hints.queues import BattleHint
_logger = getLogger('History')
_PREFS_NAME = 'displayHistory'

def _createEmptyHistory():
    return {'lastDisplayTime': {},
     'totalDisplayCount': {},
     'perBattleCount': {}}


class BattleHintsHistory(object):
    __slots__ = ('_history', '_enabled')
    ifEnabled = condition('_enabled', logFunc=LOG_WARNING, logStack=False)

    def __init__(self):
        self._history = None
        self._enabled = True
        g_playerEvents.onShowBattleHint += self._update
        g_playerEvents.onDisconnected += self.destroy
        _logger.debug('Initialized.')
        return

    def getLastDisplayTime(self, uniqueName):
        self._load()
        if self._history is None:
            _logger.debug('Can not get display time for <%s>. Not loaded.', uniqueName)
            return 0.0
        else:
            return self._history['lastDisplayTime'].get(uniqueName, 0.0)

    def getTotalDisplayCount(self, uniqueName):
        self._load()
        if self._history is None:
            _logger.debug('Can not get total display count for <%s>. Not loaded.', uniqueName)
            return 0
        else:
            return self._history['totalDisplayCount'].get(uniqueName, 0)

    def getPerBattleCount(self, uniqueName):
        self._load()
        if self._history is None:
            _logger.debug('Can not get display count per battle for <%s>. Not loaded.', uniqueName)
            return 0
        else:
            return self._history['perBattleCount'].get(uniqueName, 0)

    def destroy(self, *_, **__):
        self._enabled = False
        g_playerEvents.onShowBattleHint -= self._update
        g_playerEvents.onDisconnected -= self.destroy
        if self._history is not None:
            displayHistory = self._history
            self._history = None
            displayHistory.pop('perBattleCount')
            AccountSettings.setBattleHints(_PREFS_NAME, displayHistory)
            _logger.debug('Destroyed display history.')
        return

    @ifEnabled
    def _load(self):
        if self._history is not None or BattleReplay.isPlaying():
            return
        else:
            loadedDisplayHistory = AccountSettings.getBattleHints(_PREFS_NAME)
            if loadedDisplayHistory is None:
                self._history = _createEmptyHistory()
                _logger.debug('Created display history.')
            elif isinstance(loadedDisplayHistory, dict):
                self._history = loadedDisplayHistory
                self._history['perBattleCount'] = {}
                _logger.debug('Loaded display history.')
            else:
                self._history = _createEmptyHistory()
                _logger.debug('Corrupted display history. Reset to empty state.')
            return

    def _update(self, battleHint):
        if battleHint.model.history is None:
            return
        else:
            self._load()
            if self._history is None:
                _logger.debug('Can not update <%s> display history. Not loaded.', battleHint.uniqueName)
            else:
                prevTotalDisplayCount = self._history['totalDisplayCount'].get(battleHint.uniqueName, 0)
                prevPerBattleCount = self._history['perBattleCount'].get(battleHint.uniqueName, 0)
                self._history['lastDisplayTime'][battleHint.uniqueName] = time.time()
                self._history['totalDisplayCount'][battleHint.uniqueName] = prevTotalDisplayCount + 1
                self._history['perBattleCount'][battleHint.uniqueName] = prevPerBattleCount + 1
                _logger.debug('Hint <%s> display history updated.', battleHint.uniqueName)
            return
