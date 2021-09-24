# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EntityTimer.py
import BigWorld
import GUI
from helpers.progress_bar import ProgressBar
from script_component.ScriptComponent import DynamicScriptComponent
_PERIOD = 0.1

class EntityTimer(DynamicScriptComponent):

    def __init__(self):
        super(EntityTimer, self).__init__()
        self.__pb = pbar = ProgressBar(height=20, width=50, colour='yellow')
        self.__stick = GUI.WGStick(pbar.win, self.entity.matrix)
        self.__end = BigWorld.time()
        self.__pb.startTextUpdate(lambda : '[{:.1f}]'.format(self.__tick()), period=_PERIOD)

    def onDestroy(self):
        super(EntityTimer, self).onDestroy()
        self.__stick = None
        self.__pb.destroy()
        self.__pb = None
        return

    def __tick(self):
        return max(0.0, self.endTime - BigWorld.serverTime())
