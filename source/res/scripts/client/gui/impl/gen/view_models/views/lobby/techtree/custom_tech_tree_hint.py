# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/custom_tech_tree_hint.py
from enum import Enum
from frameworks.wulf import ViewModel

class HintIDs(Enum):
    BLUEPRINTSCONVERT = 'BlueprintsTechtreeConvertButtonHint'
    TECHTREEACTION = 'TechTreeActionStartNodeHint'


class CustomTechTreeHint(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CustomTechTreeHint, self).__init__(properties=properties, commands=commands)

    def getHintID(self):
        return HintIDs(self._getString(0))

    def setHintID(self, value):
        self._setString(0, value.value)

    def getHintText(self):
        return self._getString(1)

    def setHintText(self, value):
        self._setString(1, value)

    def getNodeID(self):
        return self._getNumber(2)

    def setNodeID(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(CustomTechTreeHint, self)._initialize()
        self._addStringProperty('hintID')
        self._addStringProperty('hintText', '')
        self._addNumberProperty('nodeID', -1)
