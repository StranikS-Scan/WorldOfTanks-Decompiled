# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/SetOrbitorPoint.py
# Compiled at: 2010-05-25 20:46:16
from FX import s_sectionProcessors
from ParticleSubSystem import *
import Pixie
from bwdebug import *

class SetOrbitorPoint(ParticleSubSystem):
    """
    This class implements an event that sets the world location of an orbitor
    to the position of the Effect source when the effect is started.
    """

    def __init__(self):
        ParticleSubSystem.__init__(self)

    def isInteresting(self, subSystem):
        act = subSystem.action(ORBITOR_PSA)
        return act != None

    def setOrbitorPoint(self, actor, source, target, subSystem):
        try:
            act = subSystem.action(ORBITOR_PSA)
            act.point = source.position
        except:
            ERROR_MSG('setOrbitorPoint has a problem with finding the position of the source object', source)

    def go(self, effect, actor, source, target, **kargs):
        self.subSystemIterate(actor, source, target, self.setOrbitorPoint)


s_sectionProcessors['SetOrbitorPoint'] = SetOrbitorPoint
