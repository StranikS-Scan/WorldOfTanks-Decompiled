# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/tooltips/role_action_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RoleActionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RoleActionModel, self).__init__(properties=properties, commands=commands)

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(RoleActionModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('description', R.invalid())
