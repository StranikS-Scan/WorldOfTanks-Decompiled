# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/user_missions_slide_model.py
from frameworks.wulf import ViewModel

class UserMissionsSlideModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(UserMissionsSlideModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getWeight(self):
        return self._getNumber(1)

    def setWeight(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(UserMissionsSlideModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('weight', 0)
