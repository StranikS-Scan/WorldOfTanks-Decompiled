# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/account_helpers/settings_core.py
import typing
if typing.TYPE_CHECKING:
    from account_helpers.settings_core.ServerSettingsManager import ServerSettingsManager

class ISettingsCache(object):
    onSyncStarted = None
    onSyncCompleted = None

    def init(self):
        raise NotImplementedError

    def isSynced(self):
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

    def applyStorages(self, restartApproved, force=False):
        raise NotImplementedError

    def confirmChanges(self, confirmators):
        raise NotImplementedError

    def clearStorages(self):
        raise NotImplementedError

    def setOverrideSettings(self, overrideDict, disableStorages):
        raise NotImplementedError

    def unsetOverrideSettings(self):
        raise NotImplementedError


class IBattleCommunicationsSettings(object):
    onChanged = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def showStickyMarkers(self):
        raise NotImplementedError

    @property
    def showInPlayerList(self):
        raise NotImplementedError

    @property
    def showCalloutMessages(self):
        raise NotImplementedError

    @property
    def showLocationMarkers(self):
        raise NotImplementedError

    @property
    def showBaseMarkers(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError
