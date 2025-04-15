# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/hb_progression_narrative_config_reader.py
from extension_utils import ResMgr
from collections import namedtuple
_CONFIG_PATH = 'historical_battles/gui/configs/historical_battles_progression_narratives.xml'
HBNarrativeConfig = namedtuple('HBNarrativeConfig', ['frontType', 'unlockLevel', 'videoSrc'])

class HBProgressionNarrativesReader(object):

    @staticmethod
    def getNarrativesData():
        narrativesConfig = ResMgr.openSection(_CONFIG_PATH + '/narratives')
        data = []
        if narrativesConfig:
            for _, section in narrativesConfig.items():
                front = section.readString('progressionFrontType')
                level = section.readInt('progressionUnlockLevel')
                videoSrc = section.readString('videoSrc')
                data.append(HBNarrativeConfig(front, level, videoSrc))

        return data
