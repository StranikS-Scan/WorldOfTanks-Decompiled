# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/AddDecal.py
# Compiled at: 2010-05-25 20:46:16
from FX.Event import Event
from FX.Event import TRANSFORM_DEPENDENT_EVENT
from FX import s_sectionProcessors
from Math import Vector3
from bwdebug import *
import BigWorld

class AddDecal(Event):
    """
    This class implements the AddDecal event,  It adds a decal to the world.
    """

    def __init__(self):
        self.decalIndex = -1
        self.decalSize = 0.0
        self.decalExtent = (0, 0, 0)

    def load(self, pSection, prereqs=None):
        """
        This method loads the AddDecal event from a data section.
        It reads decalIndex, decalSize and decalExtent from the data section.
        """
        try:
            self.decalIndex = BigWorld.decalTextureIndex(pSection.asString)
        except:
            return

        if self.decalIndex != -1:
            self.decalSize = pSection.readFloat('size', 1)
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
        if self.decalIndex == -1:
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
                BigWorld.addDecal(start, end, self.decalSize, self.decalIndex)
            except:
                ERROR_MSG('Could not add decal')

            return 0.0

    def eventTiming(self):
        return TRANSFORM_DEPENDENT_EVENT


s_sectionProcessors['AddDecal'] = AddDecal
