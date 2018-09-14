# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_tests/Navigation.py
"""
This module checks client side navigation by calculating and drawing paths.
Paths are calculated and drawn as a line of boxes.

Example usage, typed into the Python console:
import Tests.Navigation
test = Tests.Navigation.Navigation()
target = $p.position+(5,0,0)
test.testPath($p, target)

Note: you need client side enabled in the space.settings
<clientNavigation>
        <enable>        true    </enable>
</clientNavigation>
"""
import BigWorld
from bwdebug import *

class Navigation:
    DEBUG_MODEL_NAME = 'helpers/models/unit_cube.model'
    preload = BigWorld.Model(DEBUG_MODEL_NAME)

    def __init__(self):
        self._player = None
        self._debugNavPathModels = []
        return

    def __fini__(self):
        self.stopTest()

    def testPath(self, player, targetPosition):
        self._player = player
        self._moveNavPath = self._calculatePath(player.position, targetPosition)
        self._cleanupNavPathModels()
        self._attachDebugModels()

    def stopTest(self):
        self._cleanupNavPathModels()

    def _calculatePath(self, startPosition, targetPosition):
        """
        Calculate path from start to position.
        @param startPosition the start of the path.
        @param targetPosition the goal/end of path.
        @return a list of points along the path to take.
        """
        path = []
        try:
            path = BigWorld.navigatePathPoints(startPosition, targetPosition)
            DEBUG_MSG('start', startPosition)
            DEBUG_MSG('target', targetPosition)
            DEBUG_MSG('path', path)
        except ValueError as e:
            DEBUG_MSG(e)
            DEBUG_MSG('start', startPosition, 'end', targetPosition)
            path = [startPosition, targetPosition]

        return path

    def _attachDebugModels(self):
        """
        Attach a for each path point to the player.
        @param player the player to attach the models to.
        """
        for pathPoint in self._moveNavPath:
            m = BigWorld.Model(Navigation.DEBUG_MODEL_NAME)
            m.scale = (1, 1, 1)
            self._player.addModel(m)
            m.position = pathPoint
            self._debugNavPathModels.append(m)

    def _cleanupNavPathModels(self):
        """
        Remove any debug models attached to the player.
        @param player the player to clean up
        """
        if self._player is not None:
            for m in self._debugNavPathModels:
                self._player.delModel(m)

        self._debugNavPathModels = []
        return
