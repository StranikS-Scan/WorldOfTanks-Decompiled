# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Effects/OneShot.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld
from functools import partial
from _Effect import Effect
from _EventTimer import EventTimer
from FX.Event import IMMEDIATE_EVENT
from FX.Event import TRANSFORM_DEPENDENT_EVENT
from FX.Event import DURATION_DEPENDENT_EVENT
from bwdebug import *

class OneShot(Effect):
    """
    This class implements an Effect that has a simple one-play cycle.
    With this class, you call go( source, target ).  It will clean itself up
    and when completely finished, and its self.going flag will be reset.
    
    maxDuration is an important parameter, it makes sure that OneShots do
    not build up in the world.   In some cases, Effect files cannot work out
    their duration (e.g. if a continuously time-triggered particle effect is
    referenced in the effect.)  In these cases, maxDuration is used to cap the
    time the effect is in use.  If this behaviour is not desired, you should
    use FX.Persistent instead, and manage the lifetime of the effect yourself.
    
    This type of Effect does not keep a permanent assocation with any source.
    """

    def __init__(self, fileName=None, maxDuration=10.0, prereqs=None):
        Effect.__init__(self, fileName)
        Effect._create(self, prereqs)
        self.timer = EventTimer()
        self.timers = {}
        for actorName in self.actors.keys():
            self.timers[actorName] = EventTimer()

        self.maxDuration = maxDuration
        if self.maxDuration < 0.0:
            WARNING_MSG('maxDuration was negative!  setting to 10', self.maxDuration)
            self.maxDuration = 10.0

    def _playEvents(self, eventTiming, source, target=None, callbackFn=None, **kargs):
        """
        This method plays all the events that match the
        TRANSFORM_DEPENDENT_EVENT timing flag.
        
        This first pass through ( eventTiming = 0 ) happens during the
        attach frame.  this is so particles can be cleared as they are attached
        (so they don't draw in their last position for one frame.)
        
        The second pass through ( eventTiming = 1 ) happens after
        the transforms have been set, usually the next frame.  This is
        so that particles etc. can be spawned at the correct location.
        
        The third pass through ( eventTiming =2 ) happens after
        the total duration of the effect is known.  This duration is put
        into the kargs.  This is for events that either begin some stage
        through the effect, or need to end at the correct time (for example
        turning off time triggered particles for a nice fade-out,
        or setting up a colour animation that is timed exactly.)
        """
        for actorName, event in self.events:
            if event.eventTiming() == eventTiming:
                try:
                    actor = self.actors[actorName]
                except:
                    actor = None

                duration = min(event.go(self, actor, source, target, **kargs), self.maxDuration)
                if actorName != '':
                    if not self.lengths.has_key(actorName):
                        self.lengths[actorName] = duration
                    else:
                        self.lengths[actorName] = max(self.lengths[actorName], duration)
                self.totalDuration = max(duration, self.totalDuration)

        return self.totalDuration

    def go(self, source, target=None, callbackFn=None, **kargs):
        """
        This method should be the only method called on this Effect. Once fully
        finished, the self.going flag will be reset, and you can call go()
        again.
        
        If you pass in a callback function, it will be called upon full completion
        of the effect.
        """
        if self.timer.going():
            return
        self.timer.reserve()
        self.lengths = {}
        self.totalDuration = 0.0
        for actorName, attacher in self.joints.items():
            attacher.attach(self.actors[actorName], source, target)

        self._playEvents(IMMEDIATE_EVENT, source, target, callbackFn, **kargs)
        BigWorld.callback(0.001, lambda : self._go2(source, target, callbackFn, **kargs))

    def _go2(self, source, target, callbackFn, **kargs):
        """
        This method is internal - once attached and have waited a frame, spawn
        all transform dependent events.
        """
        self._playEvents(TRANSFORM_DEPENDENT_EVENT, source, target, callbackFn, **kargs)
        for actorName, duration in self.lengths.items():
            if duration <= 0.0:
                duration = self.maxDuration
                self.totalDuration = self.maxDuration
            self.timers[actorName].begin(duration, partial(self.detach, actorName, source, target))

        if self.totalDuration > self.maxDuration or self.totalDuration <= 0.0:
            WARNING_MSG('using maxDuration for this effect. perhaps this was unexpected?', self, source, target)
            self.totalDuration = self.maxDuration
        kargs['totalDuration'] = self.totalDuration
        kargs['actorDurations'] = self.lengths
        self._playEvents(DURATION_DEPENDENT_EVENT, source, target, callbackFn, **kargs)
        self.timer.begin(self.totalDuration, lambda : self.stop(source, target, callbackFn))
        self.timer.release()

    def detach(self, actorName, source, target):
        """
        This method should be considered as private for the OneShot effect. It
        is called automatically in response to the effect ending.
        """
        self.joints[actorName].detach(self.actors[actorName], source, target)

    def stop(self, source, target, callbackFn):
        if callbackFn:
            callbackFn()

    def _extendTime(self, event, duration):
        for actorName, ev in self.events:
            if event == ev:
                self.timers[actorName].extend(duration)

        self.timer.extend(duration)
