# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/SwarmTargets.py
from FX import s_sectionProcessors
from ParticleSubSystem import ParticleSubSystem
from ParticleSubSystem import MATRIX_SWARM_PSA
import Pixie

class SwarmTargets(ParticleSubSystem):
    """
    This class implements an event that sets a list of target nodes on a
    particle system containing the MatrixSwarm action.
    It loads the list of node names from XML, and binds them to the target
    model as best it can when activated.
    """

    def __init__(self):
        ParticleSubSystem.__init__(self)
        self.nodeList = []

    def load(self, pSection, prereqs = None):
        """
        This method loads a list of node names, specified by "Node" tags from
        an XML data section.
        """
        self.nodeList = pSection.readStrings('Node')
        return ParticleSubSystem.load(self, pSection)

    def isInteresting(self, subSystem):
        act = None
        try:
            act = subSystem.action(MATRIX_SWARM_PSA)
            return True
        except ValueError:
            act = None

        return act != None

    def setTargets(self, actor, source, target, subSystem):
        act = subSystem.action(MATRIX_SWARM_PSA)
        act.targets = self.targetNodes

    def go(self, effect, actor, source, target, **kargs):
        """
        This method activates the SwarmTargets event. It takes an optional
        list of target nodes via a "TargetNodes" item in the variable arguments
        dictionary.  If any run-time nodes are specified, they add to the
        existing list of load-time specified nodes.
        """
        if actor is None:
            return 0
        elif target is None:
            return 0
        else:
            nodes = []
            for i in self.nodeList:
                try:
                    try:
                        nodes.append(target.model.node(i))
                    except AttributeError:
                        nodes.append(target.node(i))

                except ValueError:
                    pass
                except TypeError:
                    nodes.append(target.root)

            if kargs.has_key('TargetNodes'):
                nodes += kargs['TargetNodes']
            if len(nodes) == 0:
                try:
                    nodes.append(target.model.root)
                except AttributeError:
                    nodes.append(target.root)

            self.targetNodes = nodes
            self.subSystemIterate(actor, source, target, self.setTargets)
            self.targetNodes = None
            return 0

    def duration(self, actor, source, target):
        pass


s_sectionProcessors['SwarmTargets'] = SwarmTargets
