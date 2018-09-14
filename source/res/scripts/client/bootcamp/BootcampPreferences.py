# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampPreferences.py
import base64
import cPickle
import BigWorld
import Settings
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from . import GAME_SETTINGS
from account_helpers.settings_core import ISettingsCore
from helpers import dependency

class BootcampPreferences(object):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        userPrefs = Settings.g_instance.userPrefs
        self.__changedFields = {}
        if not userPrefs.has_key(Settings.KEY_BOOTCAMP_PREFERENCES):
            userPrefs.write(Settings.KEY_BOOTCAMP_PREFERENCES, '')
        else:
            ds = userPrefs[Settings.KEY_BOOTCAMP_PREFERENCES]
            sDatabaseID = str(BigWorld.player().databaseID)
            if sDatabaseID != ds.readString('accountId', ''):
                ds.writeString('accountId', sDatabaseID)
                ds.writeString('changedFields', '')
            else:
                dumpedAccountSettings = ds.readString('changedFields', '')
                if dumpedAccountSettings:
                    self.__changedFields = cPickle.loads(base64.b64decode(dumpedAccountSettings))
        self.__bootcampDataSections = userPrefs[Settings.KEY_BOOTCAMP_PREFERENCES]

    def destroy(self):
        self.settingsCore.onSettingsApplied -= self.__onSettingsApplied
        self.__changedFields = None
        self.__bootcampDataSections = None
        BigWorld.savePreferences()
        return

    def setup(self, subscribeOnSettingsApplying=True):
        LOG_DEBUG_DEV_BOOTCAMP('settingsCache version: ', self.settingsCore.serverSettings.settingsCache.getVersion())
        self.settingsCore.applySettings(self.__prepareSettings())
        self.settingsCore.confirmChanges(self.settingsCore.applyStorages(restartApproved=False))
        self.settingsCore.clearStorages()
        if subscribeOnSettingsApplying:
            self.settingsCore.onSettingsApplied += self.__onSettingsApplied

    def __onSettingsApplied(self, diff):
        for k, v in diff.iteritems():
            if isinstance(v, dict):
                for _k, _v in v.iteritems():
                    self.__changedFields['{0}:{1}'.format(k, _k)] = _v

            self.__changedFields[k] = v

        self.__bootcampDataSections.write('changedFields', base64.b64encode(cPickle.dumps(self.__changedFields, -1)))

    def __prepareSettings(self):

        def _add(_container, _k, _v):
            i = _k.find(':')
            if i > -1:
                _container.setdefault(_k[:i], {})[_k[i + 1:]] = _v
            else:
                _container[_k] = _v

        toApply = {}
        for k, v in GAME_SETTINGS.iteritems():
            _add(toApply, k, v)

        for k, v in self.__changedFields.iteritems():
            _add(toApply, k, v)

        return toApply
