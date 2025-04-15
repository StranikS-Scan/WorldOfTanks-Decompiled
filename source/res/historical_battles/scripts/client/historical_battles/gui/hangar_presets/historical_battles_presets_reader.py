# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/hangar_presets/historical_battles_presets_reader.py
from gui.hangar_presets.hangar_presets_reader import DefaultPresetReader
from soft_exception import SoftException

class HistoricalBattlesPresetsReader(DefaultPresetReader):
    _CONFIG_PATH = 'historical_battles/gui/configs/historical_battles_hangar_gui_presets.xml'

    @staticmethod
    def isDefault():
        return False

    @classmethod
    def _getPreset(cls, presetName, config):
        preset = super(HistoricalBattlesPresetsReader, cls)._getPreset(presetName, config)
        if not config.has_key('hangarName'):
            raise SoftException('Missing hangarName section for {}'.format(cls._CONFIG_PATH))
        hangarName = config['hangarName'].asString
        return (preset, hangarName)

    @classmethod
    def _updateItems(cls, items, queueType, preset):
        presets = items.get(queueType, {})
        if not presets:
            items[queueType] = preset
        else:
            items[queueType].update(preset)
