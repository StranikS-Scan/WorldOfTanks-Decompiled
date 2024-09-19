# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/kpi_description_model.py
from frameworks.wulf import ViewModel

class KpiDescriptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(KpiDescriptionModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(KpiDescriptionModel, self)._initialize()
        self._addStringProperty('value', '')
        self._addStringProperty('description', '')
        self._addStringProperty('name', '')
