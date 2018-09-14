# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/CorrectMotionTriggeredParticles.py
from FX import s_sectionProcessors
from ParticleSubSystem import *
import BigWorld

class CorrectMotionTriggeredParticle(ParticleSubSystem):
    """
    This class implements an Event that resets the motion triggered flag
    on particle system actors when the effect is instantiated.  This is
    required if an effect containing motion triggered particles is to be
    reused multiple times.
    The reason for this is that the motion triggered particle source remembers
    the last position of the particle system, in order to work out exactly how
    far the particle system has travelled, and thus how many particles to
    create.  If detached from one area of the world and reattached somewhere
    else, the particle system will believe it has moved over that distance and
    create a line of unwanted particles.  This event will fix this case.    
    It only works on ParticleSystem actors.
    """

    def __init__(self):
        ParticleSubSystem.__init__(self)

    def resetMotionTriggerFlag(self, actions):
        for i in actions:
            i.motionTriggered = 1

    def isInteresting(self, subSystem):
        act = subSystem.action(SOURCE_PSA)
        return act and act.motionTriggered

    def buildActionList(self, actor, source, target, subSystem):
        act = subSystem.action(SOURCE_PSA)
        if act:
            self.actions.append(act)

    def go(self, effect, actor, source, target, **kargs):
        self.actions = []
        self.subSystemIterate(actor, source, target, self.buildActionList)
        self.resetMotionTriggerFlag(self.actions)
        BigWorld.callback(0.001, lambda : self.resetMotionTriggerFlag(self.actions))


s_sectionProcessors['CorrectMotionTriggeredParticle'] = CorrectMotionTriggeredParticle
