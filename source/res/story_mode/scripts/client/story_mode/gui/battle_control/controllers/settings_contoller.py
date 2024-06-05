# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/settings_contoller.py
import typing
import ResMgr
import section2dict
from dict2model import models, schemas, fields, validate
from gui.battle_control.arena_info.interfaces import IOverrideSettingsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache

class OverrideSettingsController(IOverrideSettingsController):
    __slots__ = ('_data',)
    _OVERRIDE_SETTINGS_PATH = 'story_mode/gui/override_settings.xml'
    settingsCore = dependency.descriptor(ISettingsCore)
    settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self):
        super(OverrideSettingsController, self).__init__()
        self._data = _overrideSettingsSchema.deserialize(section2dict.parse(ResMgr.openSection(self._OVERRIDE_SETTINGS_PATH)))

    @property
    def defaultTab(self):
        return self._data.tabSettings.defaultTab

    @property
    def disabledTabs(self):
        return self._data.tabSettings.disabledTabs

    def startControl(self, *args):
        if self.settingsCache.settings.isSynced():
            self.__onSettingsReady()
        else:
            self.settingsCore.onSettingsChanged += self.__onSettingsReady

    def stopControl(self):
        self.settingsCache.onSyncCompleted -= self.__onSettingsReady
        self.settingsCore.unsetOverrideSettings()

    def getControllerID(self):
        return BATTLE_CTRL_ID.OVERRIDE_SETTINGS

    def __onSettingsReady(self, *_):
        if not self.settingsCache.getVersion():
            return
        self.settingsCore.onSettingsChanged -= self.__onSettingsReady
        settings = {}
        storages = set()
        for control in self._data.overrides:
            storages.add(control.storage)
            if control.group:
                settings.setdefault(control.group, {})[control.option] = control.value
            settings[control.option] = control.value

        self.settingsCore.setOverrideSettings(settings, storages)


class TabSettingsModel(models.Model):
    __slots__ = ('defaultTab', 'disabledTabs')

    def __init__(self, defaultTab, disabledTabs):
        super(TabSettingsModel, self).__init__()
        self.defaultTab = defaultTab
        self.disabledTabs = disabledTabs


class OverrideControlModel(models.Model):
    __slots__ = ('storage', 'option', 'group', 'value')

    def __init__(self, storage, option, group, value):
        super(OverrideControlModel, self).__init__()
        self.storage = storage
        self.option = option
        self.group = group
        self.value = value


class OverrideSettingsModel(models.Model):
    __slots__ = ('tabSettings', 'overrides')

    def __init__(self, tabSettings, overrides):
        super(OverrideSettingsModel, self).__init__()
        self.tabSettings = tabSettings
        self.overrides = overrides


_tabSettingsSchema = schemas.Schema(fields={'defaultTab': fields.Integer(required=True),
 'disabledTabs': fields.UniCapList(fieldOrSchema=fields.Integer(required=True), required=False, default=list)}, modelClass=TabSettingsModel, checkUnknown=True)
_overrideControlSchema = schemas.Schema(fields={'storage': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'option': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'group': fields.String(required=False, default=''),
 'value': fields.Integer(required=True)}, modelClass=OverrideControlModel, checkUnknown=True)
_overrideSettingsSchema = schemas.Schema(fields={'tabSettings': fields.Nested(schema=_tabSettingsSchema),
 'overrides': fields.UniCapList(fieldOrSchema=_overrideControlSchema, required=True)}, modelClass=OverrideSettingsModel)
