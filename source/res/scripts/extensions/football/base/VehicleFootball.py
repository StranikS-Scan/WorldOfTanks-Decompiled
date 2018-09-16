# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/base/VehicleFootball.py
import BigWorld
from constants import KICK_REASON
from debug_utils import LOG_DEBUG_DEV
from wotdecorators import noexcept

class VehicleFootball(BigWorld.ScriptComponent):

    def __init__(self):
        LOG_DEBUG_DEV('[VehicleFootball] - BASE __init__')
