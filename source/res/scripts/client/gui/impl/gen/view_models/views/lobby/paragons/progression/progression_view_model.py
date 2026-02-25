# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/progression/progression_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.chapter_model import ChapterModel

class ProgressionViewModel(ViewModel):
    __slots__ = ('onPreviewVehicle', 'onCompareVehicle', 'onSelectVehicle', 'onShowVehicleInHangar', 'onPreviewStyle')
    CHAPTER_NOT_CHOSEN = -1

    def __init__(self, properties=2, commands=5):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getStages(self):
        return self._getArray(0)

    def setStages(self, value):
        self._setArray(0, value)

    @staticmethod
    def getStagesType():
        return ChapterModel

    def getCurrentStage(self):
        return self._getNumber(1)

    def setCurrentStage(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addArrayProperty('stages', Array())
        self._addNumberProperty('currentStage', 0)
        self.onPreviewVehicle = self._addCommand('onPreviewVehicle')
        self.onCompareVehicle = self._addCommand('onCompareVehicle')
        self.onSelectVehicle = self._addCommand('onSelectVehicle')
        self.onShowVehicleInHangar = self._addCommand('onShowVehicleInHangar')
        self.onPreviewStyle = self._addCommand('onPreviewStyle')
