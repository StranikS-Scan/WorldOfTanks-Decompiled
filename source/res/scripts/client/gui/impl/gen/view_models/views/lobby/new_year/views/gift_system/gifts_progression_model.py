# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_system/gifts_progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.progression_stage_model import ProgressionStageModel

class GiftsProgressionModel(ViewModel):
    __slots__ = ('onStylePreviewShow',)

    def __init__(self, properties=4, commands=1):
        super(GiftsProgressionModel, self).__init__(properties=properties, commands=commands)

    def getResetDelta(self):
        return self._getNumber(0)

    def setResetDelta(self, value):
        self._setNumber(0, value)

    def getCurrentGiftsCount(self):
        return self._getNumber(1)

    def setCurrentGiftsCount(self, value):
        self._setNumber(1, value)

    def getMaxGiftsCount(self):
        return self._getNumber(2)

    def setMaxGiftsCount(self, value):
        self._setNumber(2, value)

    def getStages(self):
        return self._getArray(3)

    def setStages(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(GiftsProgressionModel, self)._initialize()
        self._addNumberProperty('resetDelta', 0)
        self._addNumberProperty('currentGiftsCount', 0)
        self._addNumberProperty('maxGiftsCount', 0)
        self._addArrayProperty('stages', Array())
        self.onStylePreviewShow = self._addCommand('onStylePreviewShow')
