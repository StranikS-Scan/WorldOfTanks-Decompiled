# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/CelebrityConfig.py
from ny_common.settings import CelebrityConsts
from typing import Optional, Dict, Set

class CelebrityConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getQuestCount(self):
        return self._config.get(CelebrityConsts.QUEST_COUNT, 0)
