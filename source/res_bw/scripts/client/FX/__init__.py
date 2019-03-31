# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/__init__.py
# Compiled at: 2010-05-25 20:46:16
"""
This module implements a data-driven special effects framework.

It is designed to hide a lot of simple python code that is often duplicated
in entity scripts, which can frequently be error-prone.

It is designed to tie together not just particle effects, but all related
components, for example sounds, models, decals, camera shake etc.

It is also designed to implement best-practices regarding special effects
in BigWorld.  For example, it will load resources in the background to avoid
causing i/o stalls in the rendering thread.  It implements circular buffers
of often-used effects to minimise the wait time and manage memory usage.
It manages a number of conditions often encountered by special effects code,
for example, it keeps track of where effects are attached to the world, so
they can be cleaned up properly, even if the entity the effect is attached
to leaves the world during the playing of the effect.  And it allows 
customisation of the effect at run-time.

It is designed to be extensible for your game; simply implement your own
Events and register them with the class factory and they will be availble
for use by the effects system.

The FX module itself is based on 3 major interfaces; Actors, Joints and Events.

Actors represent the resources used by an effect, for example Particle Systems,
Models and Sounds.

Joints determine how the Actors are attached in the world, for example on Hard-
Points, Nodes, or assigned as Entity Models.

Events describe how the effect will play out, and there are many options to
choose from.

Note that the effects system currently does not implement a timeline for the
effect, but this would be the next most obvious extension (along with an
effects sequencer.)  Currently it only supports the concept of a random delay
for events.

Please see the file grammar guide for a description of the FX file grammar.

There are 4 main API functions the programmer needs to know about.  These are:

- FX.prerequisites().  This method returns a list of all the resources required
to be loaded before an effect can be played.  It is designed to be passed
directly into the BigWorld.loadResourceListBG() method.  The resulting resource
dictionary can then be passed directly back into the FX module to construct
effects.

- FX.OneShot().  This method creates a once-off effect, that will automatically
attach itself in the world, play the effect, and detach itself.  Once
constructed, you need to call go( source, target, args... ) on the effect.

- FX.Persistent().  This method creates an effect designed to be attached for
a long amount of time, in particular, over the course of many plays of the
effect.  Additionally it is used for effects that do not have a specified
duration, i.e. do not end by themselves.  Once constructed, you need to call
attach( source ), go( target, args... ) and detach() on the effect.

- FX.bufferedOneShot().  This method also plays a one-shot effect, but
internally it manages a fixed-size circular buffer and plays the first
available one.  This is especially important for high-frequency effects such as
bullet pchangs, where you need instantaneous access to an effect, and you
need to cap the number that may exist at any one time for memory or performance
reasons.  The FX system keeps track of how many of each type of buffered effect
was asked to play, and can report whether there was a buffer overrun, and how
large the buffer should have been in order to satisfy all requests for the
effect at any one time.

For example:

def shootGun():
        bullet = calculateTrajectory()
        target = findTarget( bullet )
        if target is not None:
                FX.bufferedOneShotEffect( "fx/fleshImpact.xml", target.model, target )
        else:
                wallCollision = findCollision( bullet )
                FX.bufferedOneShotEffect( "fx/pchang.xml", gun.model, None,                     basis = wallCollision.reflectionVector )


class Staff:
        def __init__( self ):
                self.effectName = "fx/staff_idle.xml"
                BigWorld.loadResourceListBG(                                            FX.prerequisites(self.effectName),                              self.onLoad )

        def onLoad( self, resources ):
                self.idleEffect = FX.Persistent( self.effectName, resources )


        def onEquip( self ):
                self.idleEffect.attach( self.model )
                self.idleEffect.go()


        def onUnequip( self ):
                self.idleEffect.detach()
"""
s_sectionProcessors = {}

def typeCheck(self, listOrType):
    pass


import Actors
import Events
import Joints
from Effects._Effect import prerequisites
from Effects.OneShot import OneShot
from Effects.Persistent import Persistent
from Effects.Buffered import getBufferedOneShotEffect
from Effects.Buffered import bufferedOneShotEffect
from Effects.Buffered import cleanupBufferedEffects
from Effects.Buffered import outputOverruns
