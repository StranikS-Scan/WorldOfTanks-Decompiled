# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/kpi_equip_level_data_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.main_content.kpi_item_model import KpiItemModel

class KpiEquipLevelDataModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(KpiEquipLevelDataModel, self).__init__(properties=properties, commands=commands)

    @property
    def value(self):
        return self._getViewModel(0)

    @staticmethod
    def getValueType():
        return KpiItemModel

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(KpiEquipLevelDataModel, self)._initialize()
        self._addViewModelProperty('value', KpiItemModel())
        self._addStringProperty('id', '')
