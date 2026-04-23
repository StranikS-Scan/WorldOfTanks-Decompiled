# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_repository/settings_repository.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import DYNAMIC_SETTINGS_REPOSITORY
from gui.shared.events import GUICommonEvent
from helpers.events_handler import EventsHandler
from skeletons.account_helpers.settings_repository import ISettingsProvider, ISettingsRepository, SettingsSerializable, SettingsTarget
from soft_exception import SoftException

class _ClientSettingsProvider(AccountSettings, ISettingsProvider):
    TARGET = SettingsTarget.CLIENT
    __settings = {}

    def __init__(self):
        self.__path = DYNAMIC_SETTINGS_REPOSITORY

    def get(self, name, key, default=None):
        return self.__settings.setdefault(name, _getDefaultSettings()).get(key, default)

    def set(self, name, key, value):
        self.__settings.setdefault(name, _getDefaultSettings())[key] = value

    def load(self, name):
        self.__settings[name] = AccountSettings._getValue(name, self.__path, force=True) or _getDefaultSettings()

    def dump(self, name, version):
        AccountSettings._setValue(name, self.__settings.get(name, _getDefaultSettings(version)), self.__path, force=True)

    def drop(self, name):
        AccountSettings._readSection(AccountSettings._readUserSection(), self.__path).deleteSection(name)
        if name in self.__settings:
            del self.__settings[name]

    def dropUnused(self):
        from account_helpers.settings_repository import getRegisteredSerializable
        registered = getRegisteredSerializable()[self.TARGET]
        for name in AccountSettings._readSection(AccountSettings._readUserSection(), self.__path).keys():
            if name not in registered:
                self.drop(name)


class SettingsRepository(EventsHandler, ISettingsRepository):

    def __init__(self):
        self.__settingsProviders = {}

    def init(self):
        self.__settingsProviders = {provider.TARGET:provider for provider in (_ClientSettingsProvider(),) if provider.TARGET in SettingsTarget}
        self._subscribe()

    def fini(self):
        self._unsubscribe()
        self.__settingsProviders.clear()
        del self.__settingsProviders

    def get(self, serializable, key, default=None):
        return self.__getProvider(serializable).get(serializable.getSettingsID(), key, default)

    def set(self, serializable, key, value):
        self.__getProvider(serializable).set(serializable.getSettingsID(), key, value)

    def load(self, serializable):
        provider = self.__getProvider(serializable)
        provider.load(serializable.getSettingsID())
        version = provider.get(serializable.getSettingsID(), 'version')
        if version != serializable.VERSION:
            self.drop(serializable)
            self.dump(serializable)
        provider.load(serializable.getSettingsID())

    def dump(self, serializable):
        self.__getProvider(serializable).dump(serializable.getSettingsID(), serializable.VERSION)

    def drop(self, serializable):
        self.__getProvider(serializable).drop(serializable.getSettingsID())

    def _getListeners(self):
        return ((GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited),)

    def __getProvider(self, serializable):
        if serializable.TARGET in self.__settingsProviders:
            return self.__settingsProviders[serializable.TARGET]
        raise SoftException('%s is not valid Settings target' % serializable.TARGET)

    def __onLobbyInited(self, *__, **_):
        for provider in self.__settingsProviders.values():
            provider.dropUnused()


def _getDefaultSettings(version=-1):
    return {'version': version,
     'data': {}}
