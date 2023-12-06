# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/tooltips/lootbox_tooltip_rotation.py
from frameworks.wulf import ViewSettings, Array
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.lootbox_tooltip_rotation_model import LootboxTooltipRotationModel
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_helper import isAllVehiclesObtainedInSlot
from shared_utils import first, findFirst
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.vehicle_bonus_model import VehicleBonusModel
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
from gui.shared.gui_items.Vehicle import getNationLessName

class LootboxRotationTooltip(ViewImpl):
    __slots__ = ('__lootBox', '__vehicles')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, lootBox=None):
        settings = ViewSettings(R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxRotationTooltip())
        settings.model = LootboxTooltipRotationModel()
        super(LootboxRotationTooltip, self).__init__(settings)
        self.__vehicles = []
        self.__lootBox = lootBox

    @property
    def viewModel(self):
        return super(LootboxRotationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__parseVehicleRotationLootbox()
        with self.viewModel.transaction() as vm:
            self.__setCompensation(vm)
            self.__setVehicle(vm)
            if self.__lootBox.hasLootLists():
                rotationStage = self.__lootBox.getRotationStage()
                lootLists = self.__lootBox.getLootLists()
                firstSlot = findFirst(lambda x: x is not None, lootLists[rotationStage])
                allVehiclesObtained = isAllVehiclesObtainedInSlot(lootLists[rotationStage][firstSlot], itemsCache=self.__itemsCache) if firstSlot is not None else False
                vm.setStageRotation(rotationStage + allVehiclesObtained + 1)
            else:
                vm.setStageRotation(0)
        return

    def __fillVehicle(self, model, vehicle):
        model.setName(getNationLessName(vehicle.name))
        model.setVehicleName(vehicle.shortUserName)
        model.setInInventory(vehicle.isInInventory)
        model.setWasSold(vehicle.restoreInfo is not None)
        return

    def __parseVehicleRotationLootbox(self):
        vehiclesList = []
        lootLists = self.__lootBox.getLootLists()
        for rotation in lootLists:
            vehiclesRotationList = []
            firstSlot = findFirst(lambda x: x is not None, rotation)
            if firstSlot is not None:
                for bonus in rotation[firstSlot]['bonuses']:
                    if bonus.getName() == 'vehicles':
                        vehiclesRotationList.extend((i[0] for i in bonus.getVehicles()))

                vehiclesList.append(vehiclesRotationList)

        self.__vehicles = vehiclesList
        return

    def __setCompensation(self, viewModel):
        rotation = self.__lootBox.getLootLists()[-1]
        for slot in rotation.itervalues():
            for bonus in slot['bonuses']:
                if bonus.getName() == 'vehicles':
                    firstCompensation = first((i[1]['customCompensation'] for i in bonus.getVehicles() if 'customCompensation' in i[1]))
                    if firstCompensation:
                        bonusModel = viewModel.compensation
                        amountCredits = firstCompensation[0]
                        if amountCredits:
                            bonusModel.setName(Currency.CREDITS)
                            bonusModel.setValue(str(amountCredits))
                        else:
                            bonusModel.setName(Currency.GOLD)
                            bonusModel.setValue(str(firstCompensation[1]))
                        bonusModel.setIsCompensation(True)

    def __setVehicle(self, viewModel):
        vehiclesListStage = viewModel.getVehicleStageList()
        vehiclesListStage.clear()
        for vehicles in self.__vehicles:
            vehicleInStage = Array()
            for vehicleItem in vehicles:
                vehicleModel = VehicleBonusModel()
                self.__fillVehicle(vehicleModel, vehicleItem)
                vehicleInStage.addViewModel(vehicleModel)

            vehiclesListStage.addArray(vehicleInStage)

        vehiclesListStage.invalidate()
