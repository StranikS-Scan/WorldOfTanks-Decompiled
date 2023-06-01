# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_space_listener.py
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class HangarSpaceListener(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.hangarSpace.onSpaceCreate += self._activate
        self.hangarSpace.onSpaceDestroy += self._deactivate

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self._activate
        self.hangarSpace.onSpaceDestroy -= self._deactivate

    def _activate(self):
        pass

    def _deactivate(self, inited):
        pass
