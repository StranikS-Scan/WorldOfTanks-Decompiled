# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/member_change_tankman_model.py
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel

class MemberChangeTankmanModel(TankmanModel):
    __slots__ = ()

    def __init__(self, properties=24, commands=0):
        super(MemberChangeTankmanModel, self).__init__(properties=properties, commands=commands)

    def getIsInSameVehicle(self):
        return self._getBool(23)

    def setIsInSameVehicle(self, value):
        self._setBool(23, value)

    def _initialize(self):
        super(MemberChangeTankmanModel, self)._initialize()
        self._addBoolProperty('isInSameVehicle', False)
