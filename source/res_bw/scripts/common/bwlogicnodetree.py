# Embedded file name: scripts/common/BWLogicNodeTree.py
import Math
import BigWorld

class BWLogicalNode(object):

    def __init__(self, identifier, localMatrix):
        self.localMatrix = localMatrix
        self.identifier = identifier
        self.children = []

    def addChild(self, child):
        self.children.append(child)

    def calcWorld(self, parentTransform, localMatrices, worldMatrices):
        localMatrix = localMatrices.get(self.identifier, self.localMatrix)
        worldMatrix = Math.Matrix()
        worldMatrix.set(parentTransform)
        worldMatrix.preMultiply(localMatrix)
        worldMatrices[self.identifier] = worldMatrix
        for child in self.children:
            child.calcWorld(worldMatrix, localMatrices, worldMatrices)


class BWNodeTreeTemplate(object):

    def __init__(self, dataSection):
        self.nodeList = {}
        self.root = self._loadNodes(dataSection['node'])

    def _loadNodes(self, dataSection):
        id = dataSection.readString('identifier')
        localTransform = dataSection.readMatrix('transform')
        currentNode = BWLogicalNode(id, localTransform)
        self.nodeList[id] = currentNode
        for key, val in dataSection.items():
            if key == 'node':
                currentNode.addChild(self._loadNodes(val))

        return currentNode

    def processNodes(self, parentTransform, inputs):
        outputs = {}
        self.root.calcWorld(parentTransform, inputs, outputs)
        return outputs


class BWLogicalNodeTreeLocal(object):

    def __init__(self, templateTree):
        self.input = {}
        self.templateTree = templateTree
        for id, node in self.templateTree.nodeList.items():
            self.input[id] = Math.Matrix()
            self.input[id].set(node.localMatrix)

    def processNodes(self, parentTransform):
        return self.templateTree.processNodes(parentTransform, self.input)


class BWLogicalNodeTreeLocalAndWorld(BWLogicalNodeTreeLocal):

    def __init__(self, templateTree):
        super(BWLogicalNodeTreeLocalAndWorld, self).__init__(templateTree)
        self.output = {}

    def processNodes(self, parentTransform):
        self.output = super(BWLogicalNodeTreeLocalAndWorld, self).processNodes(parentTransform)
        return self.output
