# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/sound_writers.py
from items import _xml

def writeWWTripleSoundConfig(soundConfig, section):
    _xml.rewriteString(section, 'wwsound', soundConfig.wwsound, defaultValue='')
    _xml.rewriteString(section, 'wwsoundPC', soundConfig.wwsoundPC, defaultValue='')
    _xml.rewriteString(section, 'wwsoundNPC', soundConfig.wwsoundNPC, defaultValue='')
