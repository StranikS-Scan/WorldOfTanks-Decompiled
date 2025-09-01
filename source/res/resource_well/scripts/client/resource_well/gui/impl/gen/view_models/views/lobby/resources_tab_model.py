# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/resources_tab_model.py
from frameworks.wulf import Array, ViewModel
from resource_well.gui.impl.gen.view_models.views.lobby.resource_model import ResourceModel

class ResourcesTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ResourcesTabModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getResources(self):
        return self._getArray(1)

    def setResources(self, value):
        self._setArray(1, value)

    @staticmethod
    def getResourcesType():
        return ResourceModel

    def _initialize(self):
        super(ResourcesTabModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addArrayProperty('resources', Array())
