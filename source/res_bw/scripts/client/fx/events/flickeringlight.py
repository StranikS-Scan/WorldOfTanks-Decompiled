# Embedded file name: scripts/client/FX/Events/FlickeringLight.py
import BigWorld
from FX import s_sectionProcessors
from FX.Event import Event
from FX.Event import DURATION_DEPENDENT_EVENT
from bwdebug import *
from Math import Vector4Animation
from Math import Vector4LFO
from Math import Vector4Shader
from Math import Vector4
from V4ShaderConsts import _mul
from V4ShaderConsts import _r0
from V4ShaderConsts import _r1

class DebugEventTiming(Event):

    def go(self, effect, actor, source, target, **kargs):
        DEBUG_MSG('Total duration ', kargs['totalDuration'])
        for actorName, length in kargs['actorDurations'].items():
            DEBUG_MSG('   %s ends at %0.2f seconds' % (actorName, length))

    def eventTiming(self):
        return DURATION_DEPENDENT_EVENT


s_sectionProcessors['DebugEventTiming'] = DebugEventTiming

class FlickeringLight(Event):
    """
    This class implements an Event that creates a flickering light.  It
    smoothly blends in and out depending on either the duration of the
    entire effect, or a particular actor.
    """

    def __init__(self):
        self.innerRadius = 3
        self.outerRadius = 6
        self.actorName = None
        self.colour = Vector4(255, 240, 100, 255)
        return

    def load(self, pSection, prereqs = None):
        """This method loads the FlickeringLight event from an XML data
        section.  It reads the following variables:
        - colour
        - innerRadius
        - outerRadius
        - [optional] actorForTiming
        """
        self.colour = pSection.readVector4('colour', self.colour)
        self.innerRadius = pSection.readFloat('innerRadius', self.innerRadius)
        self.outerRadius = pSection.readFloat('outerRadius', self.outerRadius)
        self.actorName = pSection.readString('actorForTiming', self.actorName)
        return self

    def go(self, effect, actor, source, target, **kargs):
        try:
            duration = kargs['actorDurations'][self.actorName]
        except:
            duration = kargs['totalDuration']

        self.light = BigWorld.PyChunkLight()
        self.light.innerRadius = self.innerRadius
        self.light.outerRadius = self.outerRadius
        self.lightFaderAnim = Vector4Animation()
        self.lightFaderAnim.time = 0
        self.lightFaderAnim.duration = duration
        col = Vector4(self.colour)
        self.lightFaderAnim.keyframes = [(0.0, (0, 0, 0, 0)),
         (0.25, col),
         (duration * 0.5, col),
         (duration, (0, 0, 0, 0))]
        lfo1 = Vector4LFO()
        lfo1.period = 0.4
        lfo2 = Vector4LFO()
        lfo2.period = 0.149
        self.lightFader = Vector4Shader()
        self.lightFader.addOp(_mul, _r1, lfo1, lfo2)
        self.lightFader.addOp(_mul, _r0, self.lightFaderAnim, _r1)
        try:
            self.light.source = source.model.root
        except:
            try:
                self.light.source = source.root
            except:
                self.light.source = source.node('Scene Root')

        self.light.visible = 1
        self.light.shader = self.lightFader
        BigWorld.callback(duration, self.removeLight)
        return duration

    def removeLight(self):
        self.light.visible = 0
        self.light.source = None
        return

    def eventTiming(self):
        return DURATION_DEPENDENT_EVENT


s_sectionProcessors['FlickeringLight'] = FlickeringLight
