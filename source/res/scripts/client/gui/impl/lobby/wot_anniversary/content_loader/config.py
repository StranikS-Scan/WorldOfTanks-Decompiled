# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/content_loader/config.py
from typing import NamedTuple, List, Dict, Optional
from shared_utils import makeTupleByDict
DayConfig = NamedTuple('DayConfig', [('id', str),
 ('image', str),
 ('imageLarge', str),
 ('video', str),
 ('localizations', str)])
BackgroundConfig = NamedTuple('BackgroundConfig', [('id', str),
 ('small', str),
 ('medium', str),
 ('large', str),
 ('extraLarge', str)])
VideosConfig = NamedTuple('VideosConfig', [('conversionOneEnv', str),
 ('conversionTwoEnvs', str),
 ('conversionThreeEnvs', str),
 ('turnPage', str)])
ContentConfig = NamedTuple('ContentConfig', [('days', List[DayConfig]), ('backgrounds', List[BackgroundConfig]), ('videos', Optional[VideosConfig])])

def makeContentConfig(data):
    videosData = data.get('videos')
    data.update({'days': [ makeTupleByDict(DayConfig, dayData) for dayData in data.get('days', []) ],
     'backgrounds': [ makeTupleByDict(BackgroundConfig, bgData) for bgData in data.get('backgrounds', []) ],
     'videos': makeTupleByDict(VideosConfig, videosData) if videosData else None})
    return makeTupleByDict(ContentConfig, data)
