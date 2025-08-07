# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/videos_resource_model.py
from frameworks.wulf import ViewModel

class VideosResourceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(VideosResourceModel, self).__init__(properties=properties, commands=commands)

    def getConversionOneEnv(self):
        return self._getString(0)

    def setConversionOneEnv(self, value):
        self._setString(0, value)

    def getConversionTwoEnvs(self):
        return self._getString(1)

    def setConversionTwoEnvs(self, value):
        self._setString(1, value)

    def getConversionThreeEnvs(self):
        return self._getString(2)

    def setConversionThreeEnvs(self, value):
        self._setString(2, value)

    def getTurnPage(self):
        return self._getString(3)

    def setTurnPage(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(VideosResourceModel, self)._initialize()
        self._addStringProperty('conversionOneEnv', '')
        self._addStringProperty('conversionTwoEnvs', '')
        self._addStringProperty('conversionThreeEnvs', '')
        self._addStringProperty('turnPage', '')
