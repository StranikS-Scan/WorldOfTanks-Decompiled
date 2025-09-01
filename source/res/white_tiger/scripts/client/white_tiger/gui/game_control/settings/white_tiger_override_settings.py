# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/settings/white_tiger_override_settings.py
import typing
import ResMgr
import section2dict
from dict2model import models, schemas, fields, validate
from debug_utils import LOG_ERROR_DEV
_CONFIG_PATH = 'white_tiger/gui/configs/white_tiger_override_settings.xml'

class WhiteTigerOverrideSettings(object):

    def __init__(self):
        self._data = None
        self.__settings = {}
        self._settingToStorage = {}
        self.__readSettingsTemplate()
        return

    @property
    def defaultTab(self):
        return self._data.tabSettings.defaultTab

    @property
    def disabledTabs(self):
        return self._data.tabSettings.disabledTabs

    @property
    def overrideSettings(self):
        return self.__settings

    def getStorageName(self, optionOrGroup):
        return self._settingToStorage.get(optionOrGroup, None)

    def __readSettingsTemplate(self):
        section = ResMgr.openSection(_CONFIG_PATH)
        if section is not None:
            self._data = _overrideSettingsSchema.deserialize(section2dict.parse(section))
        else:
            LOG_ERROR_DEV('WhiteTigerOverrideSettings could not open file ', _CONFIG_PATH)
        settingToStorage = {}
        settings = {}
        for control in self._data.overrides:
            settingToStorage[control.option] = control.storage
            if control.group:
                settings.setdefault(control.group, {})[control.option] = control.value
            settings[control.option] = control.value

        self.__settings = settings
        self._settingToStorage = settingToStorage
        return


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
