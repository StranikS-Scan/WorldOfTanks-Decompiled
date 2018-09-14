# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_5.py
from helpers.CallbackDelayer import CallbackDelayer
from bootcamp.scenery.AbstractMission import AbstractMission

class Mission5(AbstractMission):

    def __init__(self, assistant):
        super(Mission5, self).__init__(assistant)
        self.__musicCallback = CallbackDelayer()

    def destroy(self):
        super(Mission5, self).destroy()

    def start(self):
        super(Mission5, self).start()
        self.playSound2D('vo_bc_main_task')
        self.playSound2D('bc_main_tips_task_start')

    def update(self):
        super(Mission5, self).update()

    def _onPeriodChange(self, *args):
        pass
