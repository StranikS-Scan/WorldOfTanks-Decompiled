# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/main_plugins_model.py
from frameworks.wulf import ViewModel

class MainPluginsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MainPluginsModel, self).__init__(properties=properties, commands=commands)

    def getVignettePluginPath(self):
        return self._getString(0)

    def setVignettePluginPath(self, value):
        self._setString(0, value)

    def getCenterHeaderPluginPath(self):
        return self._getString(1)

    def setCenterHeaderPluginPath(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MainPluginsModel, self)._initialize()
        self._addStringProperty('vignettePluginPath', '')
        self._addStringProperty('centerHeaderPluginPath', '')
