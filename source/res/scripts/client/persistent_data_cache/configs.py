# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/persistent_data_cache/configs.py
import typing
from dict2model import models, schemas, fields
from section2dict import parse
from constants import IS_DEVELOPMENT
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
PDC_SETTINGS_KEY = 'persistent_data_cache'

class PDCSettingsModel(models.Model):
    __slots__ = ('enabled', 'devEnabled', 'useThread')

    def __init__(self, enabled, devEnabled, useThread):
        super(PDCSettingsModel, self).__init__()
        self.enabled = enabled
        self.devEnabled = devEnabled
        self.useThread = useThread

    def _reprArgs(self):
        return 'enabled={}, devEnabled={}, useThread={}'.format(self.enabled, self.devEnabled, self.useThread)


pdcSettingsSchema = schemas.Schema[PDCSettingsModel](fields={'enabled': fields.Boolean(required=False, default=True),
 'devEnabled': fields.Boolean(required=False, default=False),
 'useThread': fields.Boolean(required=False, default=True)}, checkUnknown=True, modelClass=PDCSettingsModel)

def createPDCSettings(scriptsConfig, engineConfig, userPreferences):
    raw = {}
    if scriptsConfig.has_key(PDC_SETTINGS_KEY):
        raw = parse(scriptsConfig[PDC_SETTINGS_KEY])
    elif engineConfig.has_key(PDC_SETTINGS_KEY):
        raw = parse(engineConfig[PDC_SETTINGS_KEY])
    elif IS_DEVELOPMENT:
        from gui.development.dev_settings import USER_PREF_KEY_DEVELOPMENT
        if userPreferences.has_key(USER_PREF_KEY_DEVELOPMENT) and userPreferences[USER_PREF_KEY_DEVELOPMENT].has_key(PDC_SETTINGS_KEY):
            raw = parse(userPreferences[USER_PREF_KEY_DEVELOPMENT][PDC_SETTINGS_KEY])
    return pdcSettingsSchema.deserialize(raw)
