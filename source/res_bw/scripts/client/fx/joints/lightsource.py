# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Joints/LightSource.py
from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld

class LightSource(Joint):
    """
    This class implements a Joint that attaches a light to a PyModelNode.
    
    The actor must be a PyChunkLight.
    """

    def load(self, pSection, prereqs=None):
        """
        This method loads the LightSource Joint from a data section.  The node
        name is read from the section name.
        """
        self.nodeName = pSection.asString
        return self

    def attach(self, actor, source, target=None):
        if source == None:
            return
        else:
            node = None
            if self.nodeName != '':
                try:
                    node = source.node(self.nodeName)
                except TypeError:
                    pass
                except ValueError:
                    ERROR_MSG('No such node', self.nodeName)

            try:
                if node != None:
                    actor.source = node
                else:
                    actor.source = source.root
                actor.visible = True
            except:
                ERROR_MSG('error in set light source', self, actor, source)

            return

    def detach(self, actor, source, target=None):
        actor.visible = False
        actor.source = None
        return


s_sectionProcessors['LightSource'] = LightSource
