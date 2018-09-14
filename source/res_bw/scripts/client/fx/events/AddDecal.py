# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/AddDecal.py
from FX.Event import Event
from FX.Event import TRANSFORM_DEPENDENT_EVENT
from FX import s_sectionProcessors
from Math import Vector3
from bwdebug import *
import BigWorld
BigWorld.addDecalGroup('Effects', 20.0, 200)

class AddDecal(Event):
    """
    This class implements the AddDecal event,  It adds a decal to the world.
    """

    def __init__(self):
        self.textureIndex = -1
        self.bumpTextureIndex = -1
        self.decalSize = (0.0, 0.0)
        self.decalExtent = (0, 0, 0)

    def load(self, pSection, prereqs = None):
        """
        This method loads the AddDecal event from a data section.
        It reads decalIndex, decalSize and decalExtent from the data section.
        """
        self.textureIndex = BigWorld.decalTextureIndex(pSection.readString('texture'))
        if self.textureIndex != -1:
            self.bumpTextureIndex = BigWorld.decalTextureIndex(pSection.readString('bumpTexture'))
            self.decalSize = pSection.readVector2('size', (1, 1))
            self.decalExtent = pSection.readVector3('extent', (0, -1, 0))
        else:
            WARNING_MSG('AddDecal had no associated tag')
        return self

    def go(self, effect, actor, source, target, **kargs):
        """
        This method initiates the AddDecal event.  From the variable arguments
        dictionary, it reads an "DecalInfo", which is a tuple of (start point,
        end point).
        This tuple specifies a collision ray for choosing where the decal
        should appear.
        """
        if self.textureIndex == -1:
            return
        elif source == None:
            return
        else:
            try:
                start = kargs['DecalInfo'][0]
                end = kargs['DecalInfo'][1]
            except KeyError:
                start = Vector3(source.position)
                for i in xrange(0, 3):
                    start[i] -= self.decalExtent[i] * 0.5

                end = start + self.decalExtent

            try:
                BigWorld.addDecal('Effects', start, end, self.decalSize, 0.0, self.textureIndex, self.bumpTextureIndex)
            except:
                ERROR_MSG('Could not add decal')

            return 0.0

    def eventTiming(self):
        return TRANSFORM_DEPENDENT_EVENT


s_sectionProcessors['AddDecal'] = AddDecal
