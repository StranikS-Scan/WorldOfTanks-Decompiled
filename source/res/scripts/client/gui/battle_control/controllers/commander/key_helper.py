# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/key_helper.py
import time
import Keys

class KeyHelper(object):

    def __init__(self):
        self.__lastKeyDown = Keys.KEY_NONE
        self.__lastTimeOfKeyDown = 0
        self.__numSimilarKeyDowns = 0

    def isDoublePress(self, isDown, key):
        isDoublePress = False
        if isDown:
            currentTime = int(round(time.time() * 1000))
            if key == self.__lastKeyDown and currentTime - self.__lastTimeOfKeyDown < 350:
                self.__numSimilarKeyDowns += 1
                isDoublePress = self.__numSimilarKeyDowns == 2
            else:
                self.__numSimilarKeyDowns = 1
            self.__lastKeyDown = key
            self.__lastTimeOfKeyDown = currentTime
        return isDoublePress
