# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/configs/video_subs_config_reader.py
from extension_utils import ResMgr
from collections import namedtuple
_CONFIG_PATH = 'cosmic_event/gui/video_subs_config.xml'
CosmicSubtitlePhrase = namedtuple('CosmicSubtitlePhrase', ['text', 'startTime', 'endTime'])

class CosmicVideoSubsConfigReader(object):

    @staticmethod
    def getIntroVideoPhrases():
        phrasesSection = ResMgr.openSection(_CONFIG_PATH + '/introVideo/phrases')
        data = []
        if phrasesSection:
            for _, section in phrasesSection.items():
                text = section.readString('text')
                startTime = section.readFloat('startTime')
                endTime = section.readFloat('endTime')
                data.append(CosmicSubtitlePhrase(text, startTime, endTime))

        return data
