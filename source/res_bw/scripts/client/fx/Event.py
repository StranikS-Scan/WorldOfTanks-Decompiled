# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Event.py
"""
Interface FX.Event

An event defines a single task that is played out on an actor.  It defines
5 methods that must be implemented :

- load
- go
- stop
- duration
- eventTiming

Event Timings

All FX are started over 3 frames, not just 1.

Firstly, immediate events are played.  There is nothing special to say about
these.

Secondly, transform dependent events are played.  These events require exact
knowledge of where the effect is to be played in the world.  Due to the way
nodes are accessed in python, there can be one frame between accessing a node,
and that node having a valid world transform stored in it.  Since many actors
are attached to nodes or hard-points, most events need to wait a single frame
after attachment before they play.  An example is simply spawning a particle.
If the particle system's node is not yet valid, the particles will be spawned
in the wrong spot, e.g. at the world origin.

Finally, duration dependent events are played.  These events need to know the
duration of the entire effect, before they are initiated.  An example would be
a light fade-out event that needs to be timed to finish with the rest of the
effect.
"""
IMMEDIATE_EVENT = 0
TRANSFORM_DEPENDENT_EVENT = 1
DURATION_DEPENDENT_EVENT = 2

class Event:

    def load(self, pSection, prereqs = None):
        """The method loads the event from an XML section.  The method must
        return the event that should be added to the effect, or None if the
        load failed and no event should be created."""
        return self

    def go(self, effect, actor, source, target, **kargs):
        """This method starts the event playing.  The event should return a
        time suggesting how long it will take until the event ends."""
        pass

    def stop(self, actor, source, target):
        """This method stops the event playing.  The method should return
        a time suggesting how long it will take to gracefully stop the
        event."""
        pass

    def duration(self, actor, source, target):
        """This method returns the amount of time in seconds
        the event will take to fully play out."""
        pass

    def eventTiming(self):
        """This method tells the FX system whether or not this
        event is dependent on the particle system having the
        correct location, or knowledge of total duration, or
        if it should just be played straight away."""
        return IMMEDIATE_EVENT
