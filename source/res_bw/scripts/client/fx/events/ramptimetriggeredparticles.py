# Embedded file name: scripts/client/FX/Events/RampTimeTriggeredParticles.py
from FX.Event import Event
from FX.Event import IMMEDIATE_EVENT
from FX import s_sectionProcessors
from ParticleSubSystem import *
import BigWorld
from functools import partial

class RampTimeTriggeredParticles(Event):
    """
    This class implements an event that ramps up/down the generation rate of
    time triggered particles, to fade them in/out.  It also gives them a
    specified duration, which allows time triggered particles to behave
    correctly in a OneShot effect scenario. 
    """

    def load(self, pSection, prereqs = None):
        """
        This method loads a RampTimeTriggeredParticles event from an XML
        data section.  It reads in "duration" and "fadeTime" as floats.
        """
        self.duration = pSection.readFloat('duration', 0.0)
        self.fadeTime = pSection.readFloat('fadeTime', 2.0)
        if self.duration > 0.0 and self.fadeTime > self.duration:
            self.fadeTime = self.duration / 2.0
        return self

    def saveTimes(self, actor):
        self.timeTriggeredSources = []
        for i in xrange(0, actor.nSystems()):
            try:
                source = actor.system(i).action(SOURCE_PSA)
                if source.timeTriggered:
                    self.timeTriggeredSources.append((source, source.rate))
            except:
                pass

    def restoreTimes(self, actor):
        for source, rate in self.timeTriggeredSources:
            source.rate = rate

    def setAll(self, actor, rate):
        for source, ignore in self.timeTriggeredSources:
            source.rate = rate

    def go(self, effect, actor, source, target, **kargs):
        if not hasattr(self, 'timeTriggeredSources'):
            self.saveTimes(actor)
        actor.clear()
        self.setAll(actor, 0.0)
        BigWorld.callback(0.0, partial(self.restoreTimes, actor))
        if self.duration > 0.0:
            BigWorld.callback(self.duration - self.fadeTime, partial(self.stop, actor, source, target))
        return self.duration

    def stop(self, actor, source, target):
        self.setAll(actor, 0.0)
        return self.fadeTime

    def duration(self):
        return self.duration

    def eventTiming(self):
        return IMMEDIATE_EVENT


s_sectionProcessors['RampTimeTriggeredParticles'] = RampTimeTriggeredParticles
