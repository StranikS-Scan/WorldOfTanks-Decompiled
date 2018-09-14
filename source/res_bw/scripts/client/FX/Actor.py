# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Actor.py
"""
        Interface FX.Actor

        An actor is a resource in the system, for
        example a particle system or a sound
"""

class Actor:

    def load(self, pSection, prereqs=None):
        """This method loads an actor, given a data section and optionally some
        preloaded resources.  It should return itself, or None if the actor
        failed to load."""
        return self
