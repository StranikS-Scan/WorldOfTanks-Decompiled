# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/PPAnimateProperty.py
from FX.Event import Event
from FX.Event import IMMEDIATE_EVENT
from FX import s_sectionProcessors
import Math
from Math import Vector4Animation
import PostProcessing

class PPAnimateProperty(Event):
    """
    This class implements an Event that animates a material property
    in a post-processing chain over time.
    """

    def __init__(self):
        self.animation = Math.Vector4Animation()

    def load(self, pSection, prereqs = None):
        """
        This method loads the PPAnimateProperty event from a data section.
        It reads a list of keyframes of (time,value)
        The value can currently be a Float or Vector4
        """
        self.property = pSection.asString
        self.time = 0.0
        keys = []
        for name, sect in pSection.items():
            if name == 'Key':
                self.time = sect.asFloat
                if sect.has_key('Float'):
                    f = sect.readFloat('Float')
                    value = Math.Vector4(f, f, f, f)
                elif sect.has_key('Colour'):
                    value = sect.readVector4('Colour')
                    value[0] /= 255.0
                    value[1] /= 255.0
                    value[2] /= 255.0
                    value[3] /= 255.0
                elif sect.has_key('Vector4'):
                    value = sect.readVector4('Vector4')
                keys.append((self.time, value))

        self.fkeyframes = keys
        self.rkeyframes = self.reverseKeyframes(keys)
        self.animation.keyframes = self.fkeyframes
        self.animation.duration = 1000000.0
        return self

    def reverseKeyframes(self, keyframes):
        keysCopy = list(keyframes)
        keysCopy.reverse()
        rkeyframes = []
        for time, value in keysCopy:
            rkeyframes.append((self.time - time, value))

        return rkeyframes

    def go(self, effect, actor, source, target, **kargs):
        self.animation.time = 0.0
        self.animation.keyframes = self.fkeyframes
        PostProcessing.setMaterialProperty(actor, self.property, self.animation)
        return self.time

    def stop(self, actor, source, target):
        self.animation.time = 0.0
        self.animation.keyframes = self.rkeyframes
        return self.time

    def duration(self, actor, source, target):
        return self.time

    def eventTiming(self):
        return IMMEDIATE_EVENT


s_sectionProcessors['PPAnimateProperty'] = PPAnimateProperty
