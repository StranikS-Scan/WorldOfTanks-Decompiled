# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_training/scenario_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.maps_training.maps_training_scenario_tooltip_model import MapsTrainingScenarioTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from maps_training_common.maps_training_constants import SCENARIO_INDEXES

class ScenarioTooltip(ViewImpl):

    def __init__(self, vehicleType, team, mapId, targets, vehicleName, isComplete, rewards):
        settings = ViewSettings(R.views.lobby.maps_training.ScenarioTooltip(), model=MapsTrainingScenarioTooltipModel())
        super(ScenarioTooltip, self).__init__(settings)
        self._vehicleType = vehicleType
        self._team = team
        self._mapId = mapId
        self._targets = targets
        self._vehicleName = vehicleName
        self._isComplete = isComplete
        self._rewards = rewards

    @property
    def viewModel(self):
        return super(ScenarioTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ScenarioTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setVehicleType(self._vehicleType)
        self.viewModel.setTeam(self._team)
        self.viewModel.setScenarioNum(SCENARIO_INDEXES[self._team, self._vehicleType])
        self.viewModel.setMapId(self._mapId)
        targetsModel = self.viewModel.getTargets()
        for target in self._targets:
            targetsModel.addString(target)

        self.viewModel.setVehicleName(self._vehicleName)
        self.viewModel.setIsComplete(self._isComplete)
        packer = getDefaultBonusPacker()
        bonusArray = self.viewModel.getRewards()
        for bonus in self._rewards:
            bonusList = packer.pack(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusArray.addViewModel(item)
