# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/account_helpers/settings_core.py


class ISettingsCache(object):
    onSyncStarted = None
    onSyncCompleted = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @property
    def waitForSync(self):
        raise NotImplementedError

    @property
    def settings(self):
        raise NotImplementedError

    def update(self, callback=None):
        raise NotImplementedError

    def getSectionSettings(self, section, defaultValue=0):
        raise NotImplementedError

    def setSectionSettings(self, section, value):
        raise NotImplementedError

    def setSettings(self, settings):
        raise NotImplementedError

    def getSetting(self, key, defaultValue=0):
        raise NotImplementedError

    def getVersion(self, defaultValue=0):
        raise NotImplementedError

    def setVersion(self, value):
        raise NotImplementedError

    def delSettings(self, settings):
        raise NotImplementedError


class ISettingsCore(object):
    onOnceOnlyHintsChanged = None
    onSettingsChanged = None
    onSettingsApplied = None
    onSettingsReady = None
    isReady = property()

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @isReady.getter
    def isReady(self):
        raise NotImplementedError

    @property
    def options(self):
        raise NotImplementedError

    @property
    def storages(self):
        raise NotImplementedError

    @property
    def interfaceScale(self):
        raise NotImplementedError

    @property
    def serverSettings(self):
        raise NotImplementedError

    def packSettings(self, names):
        raise NotImplementedError

    def getSetting(self, name):
        raise NotImplementedError

    def getApplyMethod(self, diff):
        raise NotImplementedError

    def applySetting(self, key, value):
        raise NotImplementedError

    def previewSetting(self, name, value):
        raise NotImplementedError

    def applySettings(self, diff):
        raise NotImplementedError

    def revertSettings(self):
        raise NotImplementedError

    def isSettingChanged(self, name, value):
        raise NotImplementedError

    def applyStorages(self, restartApproved, force=True):
        raise NotImplementedError

    def confirmChanges(self, confirmators):
        raise NotImplementedError

    def clearStorages(self, force=True):
        raise NotImplementedError

    def setEventDisabledStorages(self, storagesName):
        raise NotImplementedError

    def unsetEventDisabledStorages(self):
        raise NotImplementedError
