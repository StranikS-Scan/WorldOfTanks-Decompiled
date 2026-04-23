# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hangar_vignette_model.py
from frameworks.wulf import ViewModel

class HangarVignetteModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(HangarVignetteModel, self).__init__(properties=properties, commands=commands)

    def getFrontType(self):
        return self._getString(0)

    def setFrontType(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(HangarVignetteModel, self)._initialize()
        self._addStringProperty('frontType', '')
