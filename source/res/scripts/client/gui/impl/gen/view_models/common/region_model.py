# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/region_model.py
from frameworks.wulf import ViewModel

class RegionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RegionModel, self).__init__(properties=properties, commands=commands)

    def getRealm(self):
        return self._getString(0)

    def setRealm(self, value):
        self._setString(0, value)

    def getLanguage(self):
        return self._getString(1)

    def setLanguage(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(RegionModel, self)._initialize()
        self._addStringProperty('realm', '')
        self._addStringProperty('language', '')
