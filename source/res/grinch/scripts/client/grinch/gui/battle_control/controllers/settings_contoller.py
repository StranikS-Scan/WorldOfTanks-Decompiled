# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/battle_control/controllers/settings_contoller.py
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
    _OVERRIDE_SETTINGS_PATH = 'grinch/gui/configs/grinch_override_settings.xml'
    __settingsCore = dependency.descriptor(ISettingsCore)
    __settingsCache = dependency.descriptor(ISettingsCache)

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
        if self.__settingsCache.settings.isSynced():
            self.__onSettingsReady()
        else:
            self.__settingsCore.onSettingsChanged += self.__onSettingsReady

    def stopControl(self):
        self.__settingsCache.onSyncCompleted -= self.__onSettingsReady
        if self.__settingsCache.settings.isSynced():
            self.__settingsCore.unsetOverrideSettings()

    def getControllerID(self):
        return BATTLE_CTRL_ID.OVERRIDE_SETTINGS

    def __onSettingsReady(self, *_):
        if not self.__settingsCache.getVersion():
            return
        self.__settingsCore.onSettingsChanged -= self.__onSettingsReady
        settings = {}
        storages = set()
        for control in self._data.overrides:
            storages.add(control.storage)
            if control.group:
                settings.setdefault(control.group, {})[control.option] = control.value
            settings[control.option] = control.value

        self.__settingsCore.setOverrideSettings(settings, storages)


class _TabSettingsModel(models.Model):
    __slots__ = ('defaultTab', 'disabledTabs')

    def __init__(self, defaultTab, disabledTabs):
        super(_TabSettingsModel, self).__init__()
        self.defaultTab = defaultTab
        self.disabledTabs = disabledTabs


class _OverrideControlModel(models.Model):
    __slots__ = ('storage', 'option', 'group', 'value')

    def __init__(self, storage, option, group, value):
        super(_OverrideControlModel, self).__init__()
        self.storage = storage
        self.option = option
        self.group = group
        self.value = value


class _OverrideSettingsModel(models.Model):
    __slots__ = ('tabSettings', 'overrides')

    def __init__(self, tabSettings, overrides):
        super(_OverrideSettingsModel, self).__init__()
        self.tabSettings = tabSettings
        self.overrides = overrides


_tabSettingsSchema = schemas.Schema(fields={'defaultTab': fields.Integer(required=True),
 'disabledTabs': fields.UniCapList(fieldOrSchema=fields.Integer(required=True), required=False, default=list)}, modelClass=_TabSettingsModel, checkUnknown=True)
_overrideControlSchema = schemas.Schema(fields={'storage': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'option': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'group': fields.String(required=False, default=''),
 'value': fields.Integer(required=True)}, modelClass=_OverrideControlModel, checkUnknown=True)
_overrideSettingsSchema = schemas.Schema(fields={'tabSettings': fields.Nested(schema=_tabSettingsSchema),
 'overrides': fields.UniCapList(fieldOrSchema=_overrideControlSchema, required=True)}, modelClass=_OverrideSettingsModel)
