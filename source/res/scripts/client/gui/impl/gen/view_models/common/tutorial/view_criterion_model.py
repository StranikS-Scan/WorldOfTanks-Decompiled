# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/tutorial/view_criterion_model.py
from frameworks.wulf import ViewModel

class ViewCriterionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ViewCriterionModel, self).__init__(properties=properties, commands=commands)

    def getComponentId(self):
        return self._getString(0)

    def setComponentId(self, value):
        self._setString(0, value)

    def getViewUniqueId(self):
        return self._getString(1)

    def setViewUniqueId(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ViewCriterionModel, self)._initialize()
        self._addStringProperty('componentId', '')
        self._addStringProperty('viewUniqueId', '')
