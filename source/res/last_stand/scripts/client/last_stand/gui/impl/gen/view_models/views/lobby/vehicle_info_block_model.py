# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/vehicle_info_block_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class VehicleInfoBlockModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(VehicleInfoBlockModel, self).__init__(properties=properties, commands=commands)

    @property
    def emblem(self):
        return self._getViewModel(17)

    @staticmethod
    def getEmblemType():
        return PrestigeEmblemModel

    def getRoleKey(self):
        return self._getNumber(18)

    def setRoleKey(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(VehicleInfoBlockModel, self)._initialize()
        self._addViewModelProperty('emblem', PrestigeEmblemModel())
        self._addNumberProperty('roleKey', 0)
