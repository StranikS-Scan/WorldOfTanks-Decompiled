# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/pages/progression_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.clan_supply.clan_supply_vehicle_model import ClanSupplyVehicleModel
from gui.impl.gen.view_models.views.lobby.clan_supply.pages.stage_model import StageModel
from gui.impl.gen.view_models.views.lobby.clan_supply.stage_info_model import StageInfoModel

class ScreenStatus(IntEnum):
    PENDING = 0
    ERROR = 1
    LOADED = 2


class ProgressionModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onBuyStage', 'onSelectStage', 'onRefresh')

    def __init__(self, properties=7, commands=4):
        super(ProgressionModel, self).__init__(properties=properties, commands=commands)

    @property
    def stageInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getStageInfoType():
        return StageInfoModel

    @property
    def vehicleInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleInfoType():
        return ClanSupplyVehicleModel

    def getStatus(self):
        return ScreenStatus(self._getNumber(2))

    def setStatus(self, value):
        self._setNumber(2, value.value)

    def getSelectedStageID(self):
        return self._getNumber(3)

    def setSelectedStageID(self, value):
        self._setNumber(3, value)

    def getIsCompleted(self):
        return self._getBool(4)

    def setIsCompleted(self, value):
        self._setBool(4, value)

    def getIsMainRewardAvailable(self):
        return self._getBool(5)

    def setIsMainRewardAvailable(self, value):
        self._setBool(5, value)

    def getStages(self):
        return self._getArray(6)

    def setStages(self, value):
        self._setArray(6, value)

    @staticmethod
    def getStagesType():
        return StageModel

    def _initialize(self):
        super(ProgressionModel, self)._initialize()
        self._addViewModelProperty('stageInfo', StageInfoModel())
        self._addViewModelProperty('vehicleInfo', ClanSupplyVehicleModel())
        self._addNumberProperty('status')
        self._addNumberProperty('selectedStageID', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isMainRewardAvailable', False)
        self._addArrayProperty('stages', Array())
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onBuyStage = self._addCommand('onBuyStage')
        self.onSelectStage = self._addCommand('onSelectStage')
        self.onRefresh = self._addCommand('onRefresh')
