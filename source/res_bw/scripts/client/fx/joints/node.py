# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Joints/Node.py
from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld

class Node(Joint):
    """
    This class implements a Joint that attaches an actor to a node.
    
    The actor may be any PyAttachment, for example a model or a
    particle system.
    """

    def load(self, pSection, prereqs=None):
        """
        This method loads the Joint from a data section.  The node
        name is read from the section name.
        """
        self.nodeName = pSection.asString
        return self

    def attach(self, actor, source, target=None):
        if source is None:
            return 0
        elif actor.attached:
            ERROR_MSG('actor is already attached!', actor, self.nodeName)
            return 0
        else:
            try:
                source.model.node(self.nodeName).attach(actor)
            except AttributeError:
                try:
                    source.node(self.nodeName).attach(actor)
                except ValueError:
                    ERROR_MSG('No such node', self.nodeName)

            except ValueError:
                ERROR_MSG('No such node', self.nodeName)

            return

    def detach(self, actor, source, target=None):
        if source is None:
            return
        elif not actor.attached:
            return
        else:
            try:
                source.model.node(self.nodeName).detach(actor)
            except AttributeError:
                try:
                    source.node(self.nodeName).detach(actor)
                except ValueError:
                    ERROR_MSG('No such node', self.nodeName)

            except ValueError:
                ERROR_MSG('No such node', self.nodeName)

            return


s_sectionProcessors['Node'] = Node
