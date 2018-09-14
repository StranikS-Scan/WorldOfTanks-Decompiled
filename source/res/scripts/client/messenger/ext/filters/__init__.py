# Embedded file name: scripts/client/messenger/ext/filters/__init__.py
from gui import GUI_SETTINGS
from messenger import g_settings
from messenger.ext.filters import _chain, _collection
from messenger.storage import storage_getter

class MessageFiltersChain(_chain.FiltersChain):

    def __init__(self):
        inFilters = [{'name': 'htmlEscape',
          'filter': _collection.HtmlEscapeFilter(),
          'order': 0,
          'lock': True}]
        outFilters = [{'name': 'normalizeLobbyMessage',
          'filter': _collection.NormalizeMessageFilter(),
          'order': 0,
          'lock': False}]
        super(MessageFiltersChain, self).__init__(inFilters, outFilters)

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def init(self):
        g_settings.onUserPreferencesUpdated += self.__ms_onUserPreferencesUpdated
        self.playerCtx.onAccountAttrsChanged += self.__pc_onAccountAttrsChanged
        self.__ms_onUserPreferencesUpdated()

    def fini(self):
        g_settings.onUserPreferencesUpdated -= self.__ms_onUserPreferencesUpdated
        self.playerCtx.onAccountAttrsChanged -= self.__pc_onAccountAttrsChanged

    def __ms_onUserPreferencesUpdated(self):
        if GUI_SETTINGS.postBattleExchange.enabled:
            self.addFilter('postBattleFilter', _collection.PostBattleLinksFilter())
        if g_settings.userPrefs.enableOlFilter:
            if not self.hasFilter('enableOlFilter'):
                self.addFilter('olFilter', _collection.ObsceneLanguageFilter(), removed=['coloringOlFilter'])
        else:
            ctx = self.playerCtx
            isAdmin = ctx.isChatAdmin() or ctx.isGameAdmin()
            if isAdmin and not self.hasFilter('coloringOlFilter'):
                self.addFilter('coloringOlFilter', _collection.ColoringObsceneLanguageFilter(), removed=['olFilter'])
            else:
                self.removeFilter('olFilter')
        if g_settings.userPrefs.enableSpamFilter:
            self.addFilter('domainFilter', _collection.DomainNameFilter())
            self.addFilter('spamFilter', _collection.SpamFilter())
            self.addFilter('floodFilter', _collection.FloodFilter())
        else:
            self.removeFilter('domainFilter')
            self.removeFilter('spamFilter')
            self.removeFilter('floodFilter')

    def __pc_onAccountAttrsChanged(self):
        ctx = self.playerCtx
        if ctx.isChatAdmin() or ctx.isGameAdmin():
            if not g_settings.userPrefs.enableOlFilter and not self.hasFilter('coloringOlFilter'):
                self.addFilter('coloringOlFilter', _collection.ColoringObsceneLanguageFilter(), removed=['olFilter'])
        else:
            self.removeFilter('coloringOlFilter')


__all__ = ('MessageFiltersChain',)
