# Embedded file name: scripts/client/gui/doc_loaders/GraphicsPresetsLoader.py
import types
import BigWorld
import ResMgr
from items import _xml

class GraphicsPresetsLoader(object):
    XML_PATH = 'system/data/graphics_settings_presets.xml'
    PRESET_LABEL_TAG = 'label'
    PRESET_VALUE_TAG = 'activeOption'

    def __init__(self):
        self.__presets = {}
        self.__presetsKeys = []

    def __readXML(self, xmlCtx):
        for presetData in xmlCtx.values():
            self.__presetsKeys.append(presetData.asString)
            preset = self.__presets.setdefault(presetData.asString, {})
            for setting in presetData.values():
                if self.PRESET_LABEL_TAG in setting.keys():
                    preset[setting.readString(self.PRESET_LABEL_TAG)] = setting.readInt(self.PRESET_VALUE_TAG)

    def load(self):
        xmlCtx = ResMgr.openSection(self.XML_PATH)
        if xmlCtx is None:
            _xml.raiseWrongXml(None, self.XML_PATH, 'can not open or read')
        self.__readXML(xmlCtx)
        return

    def getPresetsKeys(self):
        return tuple(self.__presetsKeys)

    def getPreset(self, key):
        if isinstance(key, types.IntType):
            return self.__presets[self.__presetsKeys[key]]
        elif isinstance(key, types.StringType):
            return self.__presets[key]
        else:
            return None
