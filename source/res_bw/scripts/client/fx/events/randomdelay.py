# Embedded file name: scripts/client/FX/Events/RandomDelay.py
from FX.Event import Event
from FX import s_sectionProcessors
import BigWorld
import random
from bwdebug import *

class RandomDelayEvent(Event):
    """
    This class implements an event that introduces a random delay before
    activating another event or group of events.  You can specify the min/max
    delay, meaning you could also used this to implement a fixed delay event.
    If you specify multiple events, they are all spawned at the same time, i.e.
    after the specified delay.
    """

    def __init__(self):
        Event.__init__(self)
        self.events = []
        self.minDelay = 0.0
        self.maxDelay = 1.0
        self.nextDelay = 1.0

    def load(self, pSection, prereqs = None):
        """
        This method loads a RampTimeTriggeredParticles event from an XML
        data section.  It reads in "MinDelay" and "MaxDelay" as floats. All
        other sections are treated as inline events that are to be triggered
        after the specified delay.
        """
        for name, section in pSection.items():
            eventSection = pSection.items()[0][1]
            result = None
            if name not in ('MinDelay', 'MaxDelay'):
                if s_sectionProcessors.has_key(name):
                    result = s_sectionProcessors[name]().load(section)
                else:
                    ERROR_MSG('No section processor matches the tag ', name, section.asString)
                if result:
                    self.events.append(result)

        self.minDelay = pSection.readFloat('MinDelay', self.minDelay)
        self.maxDelay = pSection.readFloat('MaxDelay', self.maxDelay)
        if self.minDelay > self.maxDelay:
            ERROR_MSG('Min Delay was greater than Max Delay', self, pSection.asString)
            self.minDelay = 0.0
        self.nextDelay = self.getNextDelay()
        return self

    def getNextDelay(self):
        return random.random() * (self.maxDelay - self.minDelay) + self.minDelay

    def go(self, effect, actor, source, target, **kargs):
        duration = 0.0
        if len(self.events) > 0:
            BigWorld.callback(self.nextDelay, lambda : self.spawnEvents(effect, actor, source, target))
            return self.duration(actor, source, target)
        return self.nextDelay

    def spawnEvents(self, effect, actor, source, target):
        for i in self.events:
            i.go(effect, actor, source, target)

        self.nextDelay = self.getNextDelay()

    def duration(self, actor, source, target):
        total = self.nextDelay
        for i in self.events:
            eventDuration = i.duration(actor, source, target)
            if eventDuration >= 0.0:
                total += eventDuration

        return total


s_sectionProcessors['RandomDelayEvent'] = RandomDelayEvent
