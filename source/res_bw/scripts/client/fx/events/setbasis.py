# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/SetBasis.py
from FX import s_sectionProcessors
from ParticleSubSystem import *
from bwdebug import *

class SetBasis(ParticleSubSystem):
    """
    This class implements an Event that sets the basis vectors for a Particle
    System.
    """

    def __init__(self):
        ParticleSubSystem.__init__(self)

    def setBasis(self, actor, source, target, subSystem):
        subSystem.explicitPosition = self.worldPos
        subSystem.explicitDirection = self.worldDir

    def go(self, effect, actor, source, target, **kargs):
        """
        This method initiates the SetBasis event.  It requires a "Basis"
        parameter to be passed into the variable arguments dictionary, which
        is a tuple of (dir,pos).  Both are in world-space.
        """
        try:
            self.worldDir, self.worldPos = kargs['Basis']
            self.subSystemIterate(actor, source, target, self.setBasis)
            del self.worldDir
            del self.worldPos
        except:
            WARNING_MSG('No basis was passed into the argument list', self, actor, source, target, kargs)


s_sectionProcessors['SetBasis'] = SetBasis
