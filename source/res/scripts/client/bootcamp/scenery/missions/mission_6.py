# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_6.py
from bootcamp.scenery.AbstractMission import AbstractMission

class Mission6(AbstractMission):

    def start(self):
        super(Mission6, self).start()
        self.playSound2D('bc_music_mission_06')
        self.playSound2D('vo_bc_main_task')

    def _onPeriodChange(self, *args):
        pass
