# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/restrictions_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class RestrictionsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RestrictionsModel, self).__init__(properties=properties, commands=commands)

    def getAllowedLevels(self):
        return self._getArray(0)

    def setAllowedLevels(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(RestrictionsModel, self)._initialize()
        self._addArrayProperty('allowedLevels', Array())
