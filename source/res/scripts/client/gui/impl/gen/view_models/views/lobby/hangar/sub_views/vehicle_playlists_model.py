# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/vehicle_playlists_model.py
from frameworks.wulf import Map, ViewModel

class VehiclePlaylistsModel(ViewModel):
    __slots__ = ('onSelect', 'onCreate', 'onModify', 'onSetDirtyEdit', 'onSave', 'onDiscard', 'onDelete', 'openImportConfirm', 'openDeleteConfirm', 'onGoToAboutVehicle')

    def __init__(self, properties=4, commands=10):
        super(VehiclePlaylistsModel, self).__init__(properties=properties, commands=commands)

    def getSelectedID(self):
        return self._getString(0)

    def setSelectedID(self, value):
        self._setString(0, value)

    def getEnabled(self):
        return self._getBool(1)

    def setEnabled(self, value):
        self._setBool(1, value)

    def getDirtyEdit(self):
        return self._getBool(2)

    def setDirtyEdit(self, value):
        self._setBool(2, value)

    def getStorage(self):
        return self._getMap(3)

    def setStorage(self, value):
        self._setMap(3, value)

    @staticmethod
    def getStorageType():
        return (unicode, unicode)

    def _initialize(self):
        super(VehiclePlaylistsModel, self)._initialize()
        self._addStringProperty('selectedID', '')
        self._addBoolProperty('enabled', False)
        self._addBoolProperty('dirtyEdit', False)
        self._addMapProperty('storage', Map(unicode, unicode))
        self.onSelect = self._addCommand('onSelect')
        self.onCreate = self._addCommand('onCreate')
        self.onModify = self._addCommand('onModify')
        self.onSetDirtyEdit = self._addCommand('onSetDirtyEdit')
        self.onSave = self._addCommand('onSave')
        self.onDiscard = self._addCommand('onDiscard')
        self.onDelete = self._addCommand('onDelete')
        self.openImportConfirm = self._addCommand('openImportConfirm')
        self.openDeleteConfirm = self._addCommand('openDeleteConfirm')
        self.onGoToAboutVehicle = self._addCommand('onGoToAboutVehicle')
