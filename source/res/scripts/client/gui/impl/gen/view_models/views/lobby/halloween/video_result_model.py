# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/video_result_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.halloween.vehicle_result_model import VehicleResultModel

class VideoResultModel(ViewModel):
    __slots__ = ('onAcceptClicked', 'onCancelClicked')

    def __init__(self, properties=7, commands=2):
        super(VideoResultModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getSubTitle(self):
        return self._getResource(2)

    def setSubTitle(self, value):
        self._setResource(2, value)

    def getStageNum(self):
        return self._getNumber(3)

    def setStageNum(self, value):
        self._setNumber(3, value)

    def getIsFinalReward(self):
        return self._getBool(4)

    def setIsFinalReward(self, value):
        self._setBool(4, value)

    def getHasVehicle(self):
        return self._getBool(5)

    def setHasVehicle(self, value):
        self._setBool(5, value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    def _initialize(self):
        super(VideoResultModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleResultModel())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addNumberProperty('stageNum', 0)
        self._addBoolProperty('isFinalReward', False)
        self._addBoolProperty('hasVehicle', False)
        self._addArrayProperty('rewards', Array())
        self.onAcceptClicked = self._addCommand('onAcceptClicked')
        self.onCancelClicked = self._addCommand('onCancelClicked')
