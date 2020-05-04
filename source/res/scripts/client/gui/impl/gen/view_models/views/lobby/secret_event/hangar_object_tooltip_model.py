# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/hangar_object_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class HangarObjectTooltipModel(ViewModel):
    __slots__ = ()
    ONE = 'one'
    TWO = 'two'
    THREE = 'three'

    def __init__(self, properties=4, commands=0):
        super(HangarObjectTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getImage(self):
        return self._getResource(1)

    def setImage(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def getType(self):
        return self._getString(3)

    def setType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(HangarObjectTooltipModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addStringProperty('type', '')
