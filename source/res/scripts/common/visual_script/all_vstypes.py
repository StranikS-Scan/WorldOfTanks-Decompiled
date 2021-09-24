# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/all_vstypes.py
import BigWorld
from visual_script.type import VScriptType
from visual_script.misc import ASPECT
from visual_script.dependency import dependencyImporter
math, constants = dependencyImporter('math', 'constants')

class GameObject(VScriptType):

    def __init__(self, go):
        self.gameObject = go

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT]


class BSPCollisionModel(VScriptType):

    def __init__(self):
        self.name = ''
        self._bsp = None
        return

    def getBaseRadius(self):
        bl, tr, _ = self.model.getBoundingBox()
        a = tr[0] - bl[0]
        b = tr[2] - bl[2]
        return math.sqrt(a * a + b * b) / 2

    @property
    def model(self):
        if self._bsp is None and self.name:
            self._bsp = BigWorld.WGBspCollisionModel()
            self._bsp.setDestructibleModelName(self.name, constants.OBSTACLE_KIND.CHUNK_DESTRUCTIBLE, 0, 0)
        return self._bsp

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.SERVER]
