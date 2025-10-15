# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_ttx_item_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.params_ttx_model import ParamsTtxModel

class PortalTtxItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PortalTtxItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getParams(self):
        return self._getArray(1)

    def setParams(self, value):
        self._setArray(1, value)

    @staticmethod
    def getParamsType():
        return ParamsTtxModel

    def _initialize(self):
        super(PortalTtxItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addArrayProperty('params', Array())
