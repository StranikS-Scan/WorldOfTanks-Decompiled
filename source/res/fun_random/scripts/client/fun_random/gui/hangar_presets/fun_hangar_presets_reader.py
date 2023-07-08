# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/hangar_presets/fun_hangar_presets_reader.py
from gui.hangar_presets.hangar_presets_reader import DefaultPresetReader
from soft_exception import SoftException

class FunRandomPresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'fun_random/gui/configs/fun_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False

    @classmethod
    def _getPreset(cls, presetName, config):
        if not config.has_key('subTypes'):
            raise SoftException('Missing subTypes section for {}'.format(cls._CONFIG_PATH))
        return {subType:presetName for subType in map(int, config['subTypes'].asString.split())}

    @classmethod
    def _updateItems(cls, items, queueType, preset):
        presets = items.get(queueType, {})
        if not presets:
            items[queueType] = preset
        else:
            items[queueType].update(preset)
