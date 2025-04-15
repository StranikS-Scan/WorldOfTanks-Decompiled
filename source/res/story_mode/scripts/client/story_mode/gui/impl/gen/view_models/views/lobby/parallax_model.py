# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/parallax_model.py
from frameworks.wulf import ViewModel

class ParallaxModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(ParallaxModel, self).__init__(properties=properties, commands=commands)

    def getMissionId(self):
        return self._getNumber(0)

    def setMissionId(self, value):
        self._setNumber(0, value)

    def getParallaxStructure(self):
        return self._getString(1)

    def setParallaxStructure(self, value):
        self._setString(1, value)

    def getAtlas(self):
        return self._getString(2)

    def setAtlas(self, value):
        self._setString(2, value)

    def getPerspective(self):
        return self._getNumber(3)

    def setPerspective(self, value):
        self._setNumber(3, value)

    def getPerspectiveOriginX(self):
        return self._getNumber(4)

    def setPerspectiveOriginX(self, value):
        self._setNumber(4, value)

    def getPerspectiveOriginY(self):
        return self._getNumber(5)

    def setPerspectiveOriginY(self, value):
        self._setNumber(5, value)

    def getWrapperWidth(self):
        return self._getNumber(6)

    def setWrapperWidth(self, value):
        self._setNumber(6, value)

    def getWrapperHeight(self):
        return self._getNumber(7)

    def setWrapperHeight(self, value):
        self._setNumber(7, value)

    def getOverallScale(self):
        return self._getReal(8)

    def setOverallScale(self, value):
        self._setReal(8, value)

    def getXTilt(self):
        return self._getReal(9)

    def setXTilt(self, value):
        self._setReal(9, value)

    def getXTiltRange(self):
        return self._getReal(10)

    def setXTiltRange(self, value):
        self._setReal(10, value)

    def getYTilt(self):
        return self._getReal(11)

    def setYTilt(self, value):
        self._setReal(11, value)

    def getYTiltRange(self):
        return self._getReal(12)

    def setYTiltRange(self, value):
        self._setReal(12, value)

    def getXSlide(self):
        return self._getReal(13)

    def setXSlide(self, value):
        self._setReal(13, value)

    def getYSlide(self):
        return self._getReal(14)

    def setYSlide(self, value):
        self._setReal(14, value)

    def getChunkFileExt(self):
        return self._getString(15)

    def setChunkFileExt(self, value):
        self._setString(15, value)

    def getChunksAssetsPath(self):
        return self._getString(16)

    def setChunksAssetsPath(self, value):
        self._setString(16, value)

    def _initialize(self):
        super(ParallaxModel, self)._initialize()
        self._addNumberProperty('missionId', 0)
        self._addStringProperty('parallaxStructure', '')
        self._addStringProperty('atlas', '')
        self._addNumberProperty('perspective', 0)
        self._addNumberProperty('perspectiveOriginX', 0)
        self._addNumberProperty('perspectiveOriginY', 0)
        self._addNumberProperty('wrapperWidth', 0)
        self._addNumberProperty('wrapperHeight', 0)
        self._addRealProperty('overallScale', 0.0)
        self._addRealProperty('xTilt', 0.0)
        self._addRealProperty('xTiltRange', 0.0)
        self._addRealProperty('yTilt', 0.0)
        self._addRealProperty('yTiltRange', 0.0)
        self._addRealProperty('xSlide', 0.0)
        self._addRealProperty('ySlide', 0.0)
        self._addStringProperty('chunkFileExt', '')
        self._addStringProperty('chunksAssetsPath', '')
