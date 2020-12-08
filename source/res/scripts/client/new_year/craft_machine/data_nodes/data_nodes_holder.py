# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/data_nodes/data_nodes_holder.py


class DataNodesHolder(object):

    def __init__(self, layersCount):
        self.__nodes = {}
        self.__layers = [ [] for _ in xrange(layersCount) ]

    def __getattr__(self, nodeName):
        try:
            return self.__nodes[nodeName]
        except KeyError:
            raise AttributeError

    def clear(self):
        del self.__layers[:]
        for nodeInstance in self.__nodes.itervalues():
            nodeInstance.removeListener(self.__onNodeDataChanged)
            nodeInstance.destroy()

        self.__nodes.clear()

    def createNode(self, name, cls, layerID, *args, **kwargs):
        if name in self.__nodes:
            return False
        nodeInstance = cls(*args, **kwargs)
        nodeInstance.init(self, layerID)
        self.__nodes[name] = nodeInstance
        self.__addNodeToLayer(nodeInstance, layerID)
        nodeInstance.addListener(self.__onNodeDataChanged)
        return True

    def __addNodeToLayer(self, node, layerID):
        layer = self.__layers[layerID]
        layer.append(node)

    def __onNodeDataChanged(self, layerID):
        layersCount = len(self.__layers)
        lastLayerID = layersCount - 1
        if layerID == lastLayerID:
            return
        for layerIdx in xrange(layerID + 1, layersCount):
            layer = self.__layers[layerIdx]
            for node in layer:
                node.updateData()
