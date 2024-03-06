# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_hints/history.py
import typing
import time
import BattleReplay
from account_helpers import AccountSettings
from debug_utils import LOG_WARNING
from PlayerEvents import g_playerEvents
from gui.battle_control.controllers.battle_hints.common import getLogger
from wotdecorators import condition
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.battle_hints.queues import BattleHint
_logger = getLogger('History')
_PREFS_NAME = 'lastDisplayTime'

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
            return self._history.get(uniqueName, 0.0)

    def destroy(self, *_, **__):
        self._enabled = False
        g_playerEvents.onShowBattleHint -= self._update
        g_playerEvents.onDisconnected -= self.destroy
        if self._history is None:
            return
        else:
            history = self._history
            self._history = None
            AccountSettings.setBattleHints(_PREFS_NAME, history)
            _logger.debug('Destroyed.')
            return

    @ifEnabled
    def _load(self):
        if self._history is not None or BattleReplay.isPlaying():
            return
        else:
            loaded = AccountSettings.getBattleHints(_PREFS_NAME)
            if loaded is None:
                self._history = {}
                _logger.debug('Created.')
            elif isinstance(loaded, dict):
                self._history = loaded
                _logger.debug('Loaded.')
            else:
                self._history = {}
                _logger.debug('Corrupted. Reset to empty state.')
            return

    def _update(self, battleHint):
        if battleHint.model.history is None:
            return
        else:
            self._load()
            if self._history is None:
                _logger.debug('Can not update <%s> history. Not loaded.', battleHint.uniqueName)
                return
            self._history[battleHint.uniqueName] = time.time()
            _logger.debug('Hint <%s> last shown time updated.', battleHint.uniqueName)
            return
