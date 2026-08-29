# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/user_missions_plugin_model.py
from frameworks.wulf import Array, ViewModel

class UserMissionsPluginModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(UserMissionsPluginModel, self).__init__(properties=properties, commands=commands)

    def getUrl(self):
        return self._getString(0)

    def setUrl(self, value):
        self._setString(0, value)

    def getDependencies(self):
        return self._getArray(1)

    def setDependencies(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDependenciesType():
        return unicode

    def _initialize(self):
        super(UserMissionsPluginModel, self)._initialize()
        self._addStringProperty('url', '')
        self._addArrayProperty('dependencies', Array())
