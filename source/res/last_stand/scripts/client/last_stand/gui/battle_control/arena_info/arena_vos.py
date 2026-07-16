# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_control/arena_info/arena_vos.py
from __future__ import absolute_import
from enum import Enum

class LSKeys(Enum):
    VOIP_CONNECTED = 'voipConnected'

    @staticmethod
    def getKeys(static=True):
        return [(LSKeys.VOIP_CONNECTED, False)] if static else []

    @staticmethod
    def getSortingKeys(static=True):
        return []
