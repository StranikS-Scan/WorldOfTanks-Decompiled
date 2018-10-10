# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_space_listener.py
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class HangarSpaceListener(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.hangarSpace.onSpaceCreate += self._onSpaceCreated
        self.hangarSpace.onSpaceDestroy += self._onSpaceDestroy

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self._onSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self._onSpaceDestroy

    def _onSpaceCreated(self):
        pass

    def _onSpaceDestroy(self, inited):
        pass
