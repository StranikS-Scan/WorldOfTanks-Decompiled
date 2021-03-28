# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/tutorial/effect_model.py
from frameworks.wulf import ViewModel

class EffectModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EffectModel, self).__init__(properties=properties, commands=commands)

    def getViewId(self):
        return self._getString(0)

    def setViewId(self, value):
        self._setString(0, value)

    def getComponentId(self):
        return self._getString(1)

    def setComponentId(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def getBuilder(self):
        return self._getString(3)

    def setBuilder(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(EffectModel, self)._initialize()
        self._addStringProperty('viewId', '')
        self._addStringProperty('componentId', '')
        self._addStringProperty('type', '')
        self._addStringProperty('builder', '')
