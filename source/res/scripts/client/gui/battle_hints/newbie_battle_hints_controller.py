# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_hints/newbie_battle_hints_controller.py
import typing
import BattleReplay
from helpers import dependency
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.settings_core.settings_constants import GAME
from debug_utils import LOG_WARNING
from data_structures import VariableState
from hints_common.battle.schemas.newbie import configSchema
from hints.battle import manager as battleHintsModelsMgr
from hints.battle.newbie import getLogger
from hints.battle.schemas.newbie import NewbieClientHintModel, hintSchema
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_hints.newbie_battle_hints_controller import INewbieBattleHintsController
from skeletons.gui.shared import IItemsCache
from wotdecorators import condition
from uilogging.newbie_hints.loggers import NewbieHintsShownUILogger
if typing.TYPE_CHECKING:
    from hints_common.battle.manager import CommonBattleHintsModelsManager
    from hints.battle.schemas.base import CHMType
    from gui.battle_control.controllers.battle_hints.queues import BattleHint
_PREFS_NAME = 'battleHintsDisplayHistory'
_MISSING = VariableState('missing')
_LOCKED = VariableState('locked')
_COMPLETED = None
NEWBIE_SETTINGS_MAX_BATTLES = 50
NEWBIE_HISTORY_MAX_BATTLES = 200
_ctrlLogger = getLogger('Ctrl')
_historyLogger = getLogger('History')

class NewbieBattleHintsHistory(object):
    __slots__ = ('_history', '_updated', '_battlesCount', '_enabled')
    _itemsCache = dependency.descriptor(IItemsCache)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    ifEnabled = condition('_enabled', logFunc=LOG_WARNING, logStack=False)

    def __init__(self):
        self._history = _MISSING
        self._battlesCount = _MISSING
        self._updated = set()
        self._enabled = True
        self._itemsCache.onSyncCompleted += self._onItemsCacheUpdated
        self._connectionMgr.onDisconnected += self._onDisconnected
        g_playerEvents.onAvatarBecomeNonPlayer += self._close
        g_playerEvents.onShowBattleHint += self._update
        _historyLogger.debug('Initialized.')

    @ifEnabled
    def getDisplayCount(self, uniqueName):
        self._load()
        if self._history is _MISSING or self._history is _LOCKED or self._history is _COMPLETED:
            _historyLogger.debug('Can not get display count. Not loaded or completed.')
            return None
        else:
            return self._history.get(uniqueName, 0)

    @ifEnabled
    def reset(self):
        AccountSettings.setNewbieHints(_PREFS_NAME, {})
        self._history = _MISSING
        self._updated.clear()
        _historyLogger.debug('Reseted.')

    def destroy(self):
        self._enabled = False
        g_playerEvents.onAvatarBecomeNonPlayer -= self._close
        g_playerEvents.onShowBattleHint -= self._update
        self._itemsCache.onSyncCompleted -= self._onItemsCacheUpdated
        self._connectionMgr.onDisconnected -= self._onDisconnected
        self._onDisconnected()
        _historyLogger.debug('Destroyed.')

    @ifEnabled
    def _load(self):
        if self._history is not _MISSING or BattleReplay.isPlaying():
            return
        loaded = AccountSettings.getNewbieHints(_PREFS_NAME, default=_MISSING)
        if loaded is _MISSING:
            self._history = self._create()
            _historyLogger.debug('Created: <%s>.', self._history)
        elif not isinstance(loaded, dict) and loaded is not _COMPLETED:
            self._history = {}
            _historyLogger.debug('Corrupted. Reset to empty state.')
        else:
            self._history = loaded
            _historyLogger.debug('Loaded.')

    def _create(self):
        if self._battlesCount is _MISSING:
            return _LOCKED
        return _COMPLETED if self._battlesCount > NEWBIE_HISTORY_MAX_BATTLES else {}

    def _close(self):
        self._updated.clear()
        history = self._history
        self._history = _MISSING
        if history is _MISSING or history is _LOCKED:
            return
        modelsMgr = battleHintsModelsMgr.get()
        if history is not _COMPLETED and modelsMgr:
            if self._isCompleted(modelsMgr, history):
                history = _COMPLETED
                _historyLogger.debug('Completed.')
        AccountSettings.setNewbieHints(_PREFS_NAME, history, default=_MISSING)
        _historyLogger.debug('Closed.')

    def _update(self, battleHint):
        if not isinstance(battleHint.model, NewbieClientHintModel) or battleHint.model.history is None:
            return
        elif battleHint.uniqueName in self._updated:
            _historyLogger.debug('Can not update. <%s> already updated.', battleHint.uniqueName)
            return
        else:
            self._load()
            if self._history is _MISSING or self._history is _LOCKED or self._history is _COMPLETED:
                _historyLogger.debug('Can not update <%s>. Not loaded or completed.', battleHint.uniqueName)
                return
            self._updated.add(battleHint.uniqueName)
            self._history[battleHint.uniqueName] = self._history.get(battleHint.uniqueName, 0) + 1
            _historyLogger.debug('<%s> hint display count updated.', battleHint.uniqueName)
            return

    def _onItemsCacheUpdated(self, *args, **kwargs):
        if not self._itemsCache.items.isSynced():
            _historyLogger.debug('ItemCache items not synced.')
            return
        self._battlesCount = self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()

    def _onDisconnected(self, *args, **kwargs):
        self._close()
        self._battlesCount = _MISSING
        _historyLogger.debug('On disconnected.')

    @staticmethod
    def _isCompleted(modelsMgr, history):
        models = modelsMgr.getBySchema(hintSchema)
        for model in models:
            if model.history and model.history.displayCount > history.get(model.uniqueName, 0):
                return False

        return True


class NewbieBattleHintsController(INewbieBattleHintsController):
    _settings = dependency.descriptor(ISettingsCore)
    _settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self):
        super(NewbieBattleHintsController, self).__init__()
        self._history = NewbieBattleHintsHistory()
        self._uiLogger = NewbieHintsShownUILogger()
        self._uiLogger.initialize()
        _ctrlLogger.debug('Initialized.')

    def fini(self):
        self._uiLogger.finalize()
        self._history.destroy()
        _ctrlLogger.debug('Destroyed.')

    def isEnabled(self):
        config = configSchema.getModel()
        return bool(config and config.enabled)

    def isUserSettingEnabled(self):
        return self._settingsCache.isSynced() and bool(self._settings.getSetting(GAME.NEWBIE_BATTLE_HINTS))

    def getDisplayCount(self, uniqueName):
        if not self.isEnabled() or not self.isUserSettingEnabled():
            _historyLogger.debug('Getting display count disabled by server or user.')
            return None
        else:
            return self._history.getDisplayCount(uniqueName)

    def resetHistory(self):
        if not self.isEnabled():
            _ctrlLogger.debug('Reset history disabled by server.')
            return
        self._history.reset()
