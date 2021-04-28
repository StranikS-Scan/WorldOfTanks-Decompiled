# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamInfo.py
import BigWorld
from debug_utils import LOG_DEBUG_DEV

class TeamInfo(BigWorld.Entity):

    def __init__(self):
        LOG_DEBUG_DEV('[TeamInfo] __init__: team = {}'.format(self.teamID))

    def onEnterWorld(self, prereqs):
        LOG_DEBUG_DEV('[TeamInfo] onEnterWorld: team = {}'.format(self.teamID))
        BigWorld.player().arena.registerTeamInfo(self)

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('[TeamInfo] onLeaveWorld: team = {}'.format(self.teamID))
        BigWorld.player().arena.unregisterTeamInfo(self)
