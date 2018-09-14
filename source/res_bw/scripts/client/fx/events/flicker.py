# Embedded file name: scripts/client/FX/Events/Flicker.py
from FX.Event import Event
from FX import s_sectionProcessors
from FX.Event import IMMEDIATE_EVENT
from Math import Vector4LFO
from Math import Vector4Shader
from Math import Vector4
from Math import Vector4Animation
from V4ShaderConsts import _mul
from V4ShaderConsts import _add
from V4ShaderConsts import _r0
from V4ShaderConsts import _r1

class Flicker(Event):
    """
    This class implements an Event that flickers a light actor's colour.  It is
    a canned effect but can be customised via speed or amplitude.   
    """

    def __init__(self):
        self.colour = None
        self.lightFlicker = None
        self.amplitude = 1.0
        self.speed = 1.0
        return

    def load(self, pSection, prereqs = None):
        """This method loads the Flicker event from an XML data section.  It
        reads in two values:
        - speed ( multiplier on standard speed of the standard effect )
        - amplitude ( pct. darkening of the original colour )
        """
        self.amplitude = pSection.readFloat('amplitude', self.amplitude)
        self.speed = pSection.readFloat('speed', self.speed)
        return self

    def go(self, effect, actor, source, target, **kargs):
        self.colour = actor.colour
        lfo1 = Vector4LFO()
        lfo1.period = 0.4 / self.speed
        lfo1.amplitude = self.amplitude
        lfo2 = Vector4LFO()
        lfo2.period = 0.149 / self.speed
        scalarOffset = 1.0 - self.amplitude
        offset = Vector4(scalarOffset, scalarOffset, scalarOffset, scalarOffset)
        self.lightFlicker = Vector4Shader()
        self.lightFlicker.addOp(_mul, _r1, lfo1, lfo2)
        self.lightFlicker.addOp(_add, _r1, _r1, offset)
        self.lightFlicker.addOp(_mul, _r0, self.colour, _r1)
        actor.shader = self.lightFlicker
        return 0.0

    def stop(self, actor, source, target):
        actor.colour = self.colour
        actor.shader = None
        self.lightFlicker = None
        return 0.0

    def duration(self, actor, source, target):
        return 0.0

    def eventTiming(self):
        return IMMEDIATE_EVENT


s_sectionProcessors['Flicker'] = Flicker
