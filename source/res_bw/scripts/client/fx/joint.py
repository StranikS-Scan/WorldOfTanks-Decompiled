# Embedded file name: scripts/client/FX/Joint.py
"""
        Interface FX.Joint

        A joint is a thing that joins two things together;
        like a particle system to a hard-point.

        Because the user of an Effect should not need to know what Joints are in
        use, all Joints should allow the user to pass in an Entity, even if what
        is actually required is a node or hardpoint.  From an Entity one can
        find the desired model or node to use in the Joint - but if the user
        passes in a model or a node, one cannot find the associated     Entity.
"""

class Joint:

    def load(self, pSection, prereqs = None):
        """The method loads the joint from an XML section.  The method must
        return the joint that should be added to the effect, or None if the
        load failed and no joint could be created."""
        return self

    def attach(self, actor, source, target = None):
        """This method uses the joint to attach an actor to a source, and
        possibly a target as well."""
        pass

    def detach(self, actor, source, target = None):
        """This method asjs the joint to detach the actor from the source, and
        possibly a target as well."""
        pass
