# Embedded file name: scripts/client/FX/Events/Fade.py
from FX.Event import Event
from FX.Event import IMMEDIATE_EVENT
from FX import s_sectionProcessors
from Math import Vector4Animation

class Fade(Event):
    """
    This class implements an Event that fades a light actor's colour over
    time.  The time must be specified in the effect's XML file.
    """

    def __init__(self):
        self.colour = None
        self.time = 1.0
        return

    def load(self, pSection, prereqs = None):
        """
        This method loads the Fade event from a data section.
        It reads the time from the data section as a float.
        """
        self.time = pSection.readFloat('time', self.time)
        return self

    def go(self, effect, actor, source, target, **kargs):
        if not self.colour:
            self.colour = actor.colour
        self.lightFader = Vector4Animation()
        self.lightFader.duration = 100000.0
        self.lightFader.keyframes = [(0.0 * self.time, self.colour), (1.0 * self.time, (0, 0, 0, 0))]
        actor.shader = self.lightFader
        return self.time

    def stop(self, actor, source, target):
        actor.shader = None
        actor.colour = self.colour
        self.lightFader = None
        return 0.0

    def duration(self, actor, source, target):
        return self.time

    def eventTiming(self):
        return IMMEDIATE_EVENT


s_sectionProcessors['Fade'] = Fade
