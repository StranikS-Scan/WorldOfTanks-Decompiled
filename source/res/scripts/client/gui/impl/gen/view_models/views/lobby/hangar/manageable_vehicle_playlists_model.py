# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/manageable_vehicle_playlists_model.py
from frameworks.wulf import ViewModel

class ManageableVehiclePlaylistsModel(ViewModel):
    __slots__ = ('onReset', 'onSelectVehicle')
    INVALID_VEHICLE_INTCD = -1

    def __init__(self, properties=1, commands=2):
        super(ManageableVehiclePlaylistsModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(0)

    def setIntCD(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(ManageableVehiclePlaylistsModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self.onReset = self._addCommand('onReset')
        self.onSelectVehicle = self._addCommand('onSelectVehicle')
