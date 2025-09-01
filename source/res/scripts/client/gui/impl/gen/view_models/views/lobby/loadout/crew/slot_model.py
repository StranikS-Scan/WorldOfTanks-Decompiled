# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/crew/slot_model.py
from frameworks.wulf import Array, ViewModel

class SlotModel(ViewModel):
    __slots__ = ()
    COMMANDER_ROLE = 'commander'
    RADIOMAN_ROLE = 'radioman'
    DRIVER_ROLE = 'driver'
    GUNNER_ROLE = 'gunner'
    LOADER_ROLE = 'loader'

    def __init__(self, properties=3, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getTankmanId(self):
        return self._getNumber(1)

    def setTankmanId(self, value):
        self._setNumber(1, value)

    def getRoles(self):
        return self._getArray(2)

    def setRoles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRolesType():
        return unicode

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('tankmanId', -1)
        self._addArrayProperty('roles', Array())
