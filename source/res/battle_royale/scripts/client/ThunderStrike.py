# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/ThunderStrike.py
import BigWorld
from Event import Event
from helpers.CallbackDelayer import CallbackDelayer
from debug_utils import LOG_DEBUG_DEV

class ThunderStrike(BigWorld.Entity, CallbackDelayer):

    def __init__(self):
        super(ThunderStrike, self).__init__()
        LOG_DEBUG_DEV('ArenaInfoThunderStrikeLauncher launched', self.position, self.equipmentID)
        self.onHit = Event()

    def hitThunderStrike(self):
        LOG_DEBUG_DEV('hitThunderStrike')
        self.onHit()
