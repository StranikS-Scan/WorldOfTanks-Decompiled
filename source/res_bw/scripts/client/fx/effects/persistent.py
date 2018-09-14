# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Effects/Persistent.py
import BigWorld
from _Effect import Effect
from _EventTimer import EventTimer

class Persistent(Effect):
    """
    This class implements an Effect that persist on an object.
    With this class, you must call attach(), then go(),stop(),go(),stop() as
    many times as you like, then detach().
    
    Once attached, there is a persistent association with the source.  Thus
    when calling go(), you need not pass in the source again.
    
    You can pass in a callback fn to go(), which is called back when the effect
    has properly finished one pass through for all its events.
    """

    def __init__(self, fileName=None, prereqs=None):
        Effect.__init__(self, fileName)
        Effect._create(self, prereqs)
        self.timer = EventTimer()
        self.source = None
        self.target = None
        return

    def attach(self, source):
        """
        This method attaches the effect to the source.  The source may be a
        model or an entity, depending on the effect.  It is usually safe to
        pass in an Entity, since the Joints associated with the effect can
        find the appropriate model and/or node from an entity, however Joints
        cannot derive the entity given a model or a node.
        """
        self.source = source
        for actor, attacher in self.joints.items():
            attacher.attach(self.actors[actor], source)

    def go(self, target=None, callbackFn=None, **kargs):
        """
        This method starts the effect playing, once it is attached.  You may
        call go() and stop() any number of times in between attach() and
        detach() pairs.
        """
        self.totalDuration = 0.0
        self.target = target
        for actorName, event in self.events:
            if event.eventTiming() == 0:
                try:
                    actor = self.actors[actorName]
                except:
                    actor = None

                self.totalDuration = max(self.totalDuration, event.go(self, actor, self.source, target, **kargs))

        BigWorld.callback(0.001, lambda : self._go2(target, callbackFn, **kargs))
        return

    def _go2(self, target=None, callbackFn=None, **kargs):
        for actorName, event in self.events:
            if event.eventTiming() > 0:
                try:
                    actor = self.actors[actorName]
                except:
                    actor = None

                self.totalDuration = max(self.totalDuration, event.go(self, actor, self.source, target, **kargs))

        if callbackFn:
            self.timer.begin(self.totalDuration + 0.001, callbackFn)
        return

    def stop(self):
        """
        This method stops the effect playing.  Note that it will do this
        gracefully, i.e. it allows the effect to die out rather than pop out.
        For this reason, a stopTime is returned and the effect should not
        be started again, nor should it be detached, until this time has been
        has been allowed to pass.
        """
        stopTime = 0.0
        for actorName, event in self.events:
            try:
                actor = self.actors[actorName]
            except KeyError:
                actor = None

            eventStopTime = event.stop(actor, self.source, self.target)
            stopTime = max(stopTime, eventStopTime)

        return stopTime

    def detach(self):
        """
        This method detaches the effect from the source, removing it and all
        its actors from the world.  The effect remembers where it was
        attached to begin with, so no arguments need be passed in.
        """
        for actor, attacher in self.joints.items():
            attacher.detach(self.actors[actor], self.source)

        self.source = None
        self.target = None
        return
