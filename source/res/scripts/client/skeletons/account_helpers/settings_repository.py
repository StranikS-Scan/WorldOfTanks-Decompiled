# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/account_helpers/settings_repository.py
from enum import Enum
from typing import TYPE_CHECKING
from helpers import dependency
from shared_utils import getFullClassName
if TYPE_CHECKING:
    from typing import Any, Optional

class SettingsTarget(Enum):
    CLIENT = 'client'


class ISettingsProvider(object):
    TARGET = None

    def get(self, name, key, default=None):
        raise NotImplementedError

    def set(self, name, key, value):
        raise NotImplementedError

    def load(self, name):
        raise NotImplementedError

    def dump(self, name, version):
        raise NotImplementedError

    def drop(self, name):
        raise NotImplementedError

    def dropUnused(self):
        raise NotImplementedError


class ISettingsRepository(object):

    def get(self, name, key, default=None):
        raise NotImplementedError

    def set(self, name, key, value):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def load(self, settingsSerializable):
        raise NotImplementedError

    def dump(self, settingsSerializable):
        raise NotImplementedError

    def drop(self, settingsSerializable):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class SettingsSerializable(object):
    TARGET = SettingsTarget.CLIENT
    VERSION = 0
    __settingsRepository = dependency.descriptor(ISettingsRepository)

    @classmethod
    def getSettingsID(cls):
        return getFullClassName(cls)

    def getSetting(self, key, default=None):
        return self.__settingsRepository.get(self, key, default)

    def setSetting(self, key, value):
        self.__settingsRepository.set(self, key, value)

    def _loadSettings(self):
        self.__settingsRepository.load(self)

    def _dumpSettings(self):
        self.__settingsRepository.dump(self)
