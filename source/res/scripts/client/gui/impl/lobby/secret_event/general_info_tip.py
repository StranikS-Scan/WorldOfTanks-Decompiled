# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/general_info_tip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.general_tooltip_list_item_model import GeneralTooltipListItemModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_tooltip_model import GeneralTooltipModel
from gui.impl.lobby.secret_event import ProgressMixin, VehicleMixin, AbilitiesMixin
from gui.impl.pub import ViewImpl
from gui.prb_control.dispatcher import g_prbLoader
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController

class GeneralInfoTip(ViewImpl, ProgressMixin, VehicleMixin, AbilitiesMixin):
    __slots__ = ('__generalId', '__generalProgress', '__tooltipType')
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID, generalId, tooltipType=GeneralTooltipModel.DEFAULT):
        settings = ViewSettings(layoutID)
        settings.model = GeneralTooltipModel()
        super(GeneralInfoTip, self).__init__(settings)
        self.__generalId = int(generalId)
        self.__tooltipType = tooltipType
        self.__generalProgress = self.gameEventController.getCommander(self.__generalId)

    @property
    def viewModel(self):
        return super(GeneralInfoTip, self).getViewModel()

    def _onLoading(self):
        super(GeneralInfoTip, self)._onLoading()
        generalId = self.__generalId
        self.viewModel.setType(self.__tooltipType)
        self.viewModel.setId(generalId)
        self.viewModel.setName(R.strings.event.unit.name.num(generalId)())
        self.viewModel.setDescription(R.strings.event.unit.description.num(generalId)())
        generalProgress = self.__generalProgress
        progressionData = self.getCurrentProgressionData(generalProgress)
        currentLevel = None
        if self.__tooltipType == GeneralTooltipModel.STATIC:
            self.viewModel.setProgress(0)
            self.viewModel.setProgressMax(0)
            self.viewModel.setGeneralLevel(generalProgress.getRealMaxLevel())
            currentLevel = generalProgress.getMaxLevel()
        else:
            self.viewModel.setProgress(progressionData.currentProgress)
            self.viewModel.setProgressMax(progressionData.maxProgress)
            self.viewModel.setGeneralLevel(progressionData.level)
            currentEnergy = self.gameEventController.getCommander(generalId).getCurrentEnergy()
            if currentEnergy:
                self.viewModel.setOrderLabel(currentEnergy.getLabel())
            self.viewModel.setStatus(self.__getStatus(generalId))
        vehicles = self.viewModel.getVehicleList()
        for idx, vehicleData in enumerate(self.getVehicleData(generalProgress, currentLevel), 1):
            vm = GeneralTooltipListItemModel()
            vehicleIconName = vehicleData.vehicle.name.split(':', 1)[-1].replace('-', '_')
            vm.setIcon(R.images.gui.maps.icons.secretEvent.vehicles.c_48x48.dyn(vehicleIconName)())
            vm.setText(vehicleData.vehicle.userName)
            vm.setIsDisabled(not vehicleData.isCurrent)
            vm.setIsLocked(not vehicleData.isUnlocked)
            vm.setLevel(idx)
            vehicles.addViewModel(vm)
            if vehicleData.isCurrent:
                self.viewModel.setVehicleType(vehicleData.vehicle.type)

        skills = self.viewModel.getSkillList()
        for abilitiesData in self.getAbilitiesData(generalProgress, currentLevel=currentLevel, maxLevel=currentLevel):
            vm = GeneralTooltipListItemModel()
            vm.setIcon(abilitiesData.iconDynAccessor())
            vm.setText(abilitiesData.name)
            vm.setIsDisabled(not abilitiesData.isEnabled)
            vm.setIsLocked(not abilitiesData.isEnabled)
            vm.setLevel(abilitiesData.level)
            skills.addViewModel(vm)

        return

    def __getStatus(self, generalID):
        commander = self.gameEventController.getCommander(generalID)
        if commander is not None:
            if commander.isLocked():
                return GeneralTooltipModel.IN_BATTLE
            dispatcher = g_prbLoader.getDispatcher()
            isSelected = self.gameEventController.getSelectedCommanderID() == generalID
            if dispatcher is not None and isSelected and dispatcher.getPlayerInfo().isReady:
                return GeneralTooltipModel.IN_PLATOON
        return GeneralTooltipModel.READY
