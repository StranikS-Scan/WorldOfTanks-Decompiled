# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/SetColour.py
from FX import s_sectionProcessors
from ParticleSubSystem import *
from bwdebug import *

class SetColour(ParticleSubSystem):
    """
    This class implements an event that sets a colour modulator onto the
    Tint Shader of any particle sub system.  This multiplies a given colour
    with the particle systems' tint shader colour animation.  It is designed
    for run-time manipulation, and as such only takes colour passed into
    the run-time variable arguments, and does not support loading a colour
    from XML.
    """

    def __init__(self):
        ParticleSubSystem.__init__(self)

    def isInteresting(self, subSystem):
        act = subSystem.action(TINT_SHADER_PSA)
        return act != None

    def setModulator(self, actor, source, target, subSystem):
        act = subSystem.action(TINT_SHADER_PSA)
        act.modulator = self.colour

    def go(self, effect, actor, source, target, **kargs):
        """
        This method initiates the SetColour event.  It requires a "SetColour"
        parameter to be passed into the variable arguments dictionary, which
        can be any Vector4Provider.
        """
        try:
            self.colour = kargs['SetColour']
            self.subSystemIterate(actor, source, target, self.setModulator)
        except:
            WARNING_MSG('No colour was passed into the argument list', self, actor, source, target, kargs)


s_sectionProcessors['SetColour'] = SetColour
