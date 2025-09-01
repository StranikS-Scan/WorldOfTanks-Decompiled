# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/router_model.py
from frameworks.wulf import ViewModel

class RouterModel(ViewModel):
    __slots__ = ('navigateTo', 'navigateBack')

    def __init__(self, properties=2, commands=2):
        super(RouterModel, self).__init__(properties=properties, commands=commands)

    def getRoute(self):
        return self._getString(0)

    def setRoute(self, value):
        self._setString(0, value)

    def getParams(self):
        return self._getString(1)

    def setParams(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(RouterModel, self)._initialize()
        self._addStringProperty('route', '')
        self._addStringProperty('params', '')
        self.navigateTo = self._addCommand('navigateTo')
        self.navigateBack = self._addCommand('navigateBack')
