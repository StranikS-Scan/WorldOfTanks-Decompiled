# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_6.py
import BigWorld
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
import SoundGroups
from bootcamp.scenery.AbstractMission import AbstractMission

class Mission6(AbstractMission):

    def __init__(self, assistant):
        super(Mission6, self).__init__(assistant)

    def destroy(self):
        super(Mission6, self).destroy()

    def start(self):
        super(Mission6, self).start()
        self.playSound2D('bc_music_mission_06')
        self.playSound2D('vo_bc_main_task')

    def update(self):
        super(Mission6, self).update()
