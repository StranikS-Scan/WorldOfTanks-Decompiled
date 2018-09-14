# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Actors/Light.py
import BigWorld
from bwdebug import *
from FX.Actor import Actor
from FX import s_sectionProcessors

class Light(Actor):
    """
    This class implements an Actor that is a PyChunkLight.
    """

    def load(self, pSection, prereqs = None):
        """
        This method loads a PyChunkLight from a data section. The
        the light reads its innerRadius, outerRadius and colour from the
        data section.
        """
        try:
            actor = BigWorld.PyChunkLight()
            actor.innerRadius = pSection.readFloat('innerRadius', 0)
            actor.outerRadius = pSection.readFloat('outerRadius', 10)
            actor.colour = pSection.readVector4('colour', (255, 255, 255, 255))
            actor.priority = pSection.readInt('priority', 0)
        except:
            ERROR_MSG('Could not create Light', pSection.asString)
            actor = None

        return actor


s_sectionProcessors['Light'] = Light
