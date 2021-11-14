# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/statuses/controller_mixin.py
import typing
import operator
from functools import partial
from PlayerEvents import g_playerEvents
from gui.platform.base.statuses.status import Status
from gui.platform.base.statuses.constants import StatusTypes, DEFAULT_CONTEXT
from gui.platform.base.statuses.events_mgr import StatusEventsManager
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class StatusesMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    DEFAULT_STATUS = Status(StatusTypes.UNDEFINED)

    def __init__(self):
        super(StatusesMixin, self).__init__()
        self._statuses = {}
        self._statusEventsMgr = StatusEventsManager()
        self._statusTokens = self._getStatusTokensSettings()

    def fini(self):
        self._statusEventsMgr.clear()
        super(StatusesMixin, self).fini()

    @property
    def statusEvents(self):
        return self._statusEventsMgr

    def getCurrentStatus(self, context=DEFAULT_CONTEXT):
        return self._getStatus(context).type

    def _start(self):
        self._statuses.clear()
        super(StatusesMixin, self)._start()
        g_playerEvents.onClientUpdated += self._onClientUpdated
        self.itemsCache.onSyncCompleted += self._checkStatusTokens
        self.lobbyContext.onServerSettingsChanged += self._onServerSettingsChanged
        self._serverSettings.onServerSettingsChange += self._checkIsEnabled

    def _stop(self):
        super(StatusesMixin, self)._stop()
        self._statuses.clear()
        g_playerEvents.onClientUpdated -= self._onClientUpdated
        self.itemsCache.onSyncCompleted -= self._checkStatusTokens
        self.lobbyContext.onServerSettingsChanged -= self._onServerSettingsChanged
        self._serverSettings.onServerSettingsChange -= self._checkIsEnabled

    def _getStatus(self, context=DEFAULT_CONTEXT):
        return self._statuses.get(context, self.DEFAULT_STATUS)

    def _updateStatus(self, status, context=DEFAULT_CONTEXT):
        current = self._getStatus(context=context)
        if current == status:
            self._logger.debug('Status: (%s|%s) not changed.', context, current)
            return
        self._logger.debug('Status for context %s changed from %s to %s.', context, current, status)
        self._statuses[context] = status
        self._statusEventsMgr.send(status, context=context)

    def _checkStatusTokens(self, *args, **kwargs):
        self._processStatusTokens(self.itemsCache.items.tokens.isTokenAvailable)
        self.itemsCache.onSyncCompleted -= self._checkStatusTokens

    def _onClientUpdated(self, diff, _):
        tokensDiff = diff.get('tokens')
        if tokensDiff is not None:
            self._processStatusTokens(partial(operator.contains, tokensDiff))
        return

    @property
    def _serverSettings(self):
        return self.lobbyContext.getServerSettings()

    def _onServerSettingsChanged(self, *_):
        self._serverSettings.onServerSettingsChange += self._checkIsEnabled

    def _checkIsEnabled(self, _):
        if not self.settings.isEnabled():
            self._updateStatus(Status(StatusTypes.UNDEFINED), context=DEFAULT_CONTEXT)

    def _getStatusTokensSettings(self):
        return []

    def _processStatusTokens(self, validator):
        for token, context, status in self._statusTokens:
            if validator(token):
                status = status() if callable(status) else status
                self._logger.debug('Token (%s|%s) received.', context, token)
                self._updateStatus(status, context=context)
                break
