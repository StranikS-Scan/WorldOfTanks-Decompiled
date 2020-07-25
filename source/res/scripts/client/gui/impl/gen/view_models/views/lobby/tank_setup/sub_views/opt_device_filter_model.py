# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/opt_device_filter_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.filters_model import FiltersModel

class OptDeviceFilterModel(FiltersModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=2):
        super(OptDeviceFilterModel, self).__init__(properties=properties, commands=commands)

    def getSpecializationHintEnabled(self):
        return self._getString(4)

    def setSpecializationHintEnabled(self, value):
        self._setString(4, value)

    def getSelectedCount(self):
        return self._getNumber(5)

    def setSelectedCount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(OptDeviceFilterModel, self)._initialize()
        self._addStringProperty('specializationHintEnabled', '')
        self._addNumberProperty('selectedCount', 0)
