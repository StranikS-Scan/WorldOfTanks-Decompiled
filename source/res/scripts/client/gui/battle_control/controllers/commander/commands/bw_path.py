# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/commands/bw_path.py
import BigWorld

class BWPath(object):
    __WIDTH = 0.25
    __DIRECT_MOVE_COLOR = (255, 255, 255, 255)
    __AUTONOMOUS_MOVE_COLOR = (255, 249, 94, 128)
    __TICK_RATE = 5

    def __init__(self, vID, isAutonomous=False):
        self.__makePathName = 'tp_{}'.format(vID)
        self.__path = None
        self.__tick = 0
        self.__color = BWPath.__AUTONOMOUS_MOVE_COLOR
        self.__nextColor = self._getPathColor(isAutonomous)
        self.__targetPos = None
        return

    def removePath(self):
        BigWorld.tankPathRemove(BigWorld.player().spaceID, self.__makePathName)

    def setIsAutonomousMove(self, isAutonomousMove):
        self.__nextColor = self._getPathColor(isAutonomousMove)

    def tick(self, startPos, tail):
        if self.__tick < self.__TICK_RATE:
            self.__tick += 1
            return
        self.__tick = 0
        newPath = (startPos, tail)
        if newPath == self.__path:
            return
        self.__path = newPath
        if tail:
            newTarget = tail[-1]
            if self.__targetPos != newTarget:
                self.__targetPos = newTarget
                self.__color = self.__nextColor
            BigWorld.tankPathAdd(BigWorld.player().spaceID, self.__makePathName, startPos, tail, self.__color, self.__WIDTH)
        else:
            self.removePath()

    @staticmethod
    def _getPathColor(isAutonomousMove):
        return BWPath.__AUTONOMOUS_MOVE_COLOR if isAutonomousMove else BWPath.__DIRECT_MOVE_COLOR
