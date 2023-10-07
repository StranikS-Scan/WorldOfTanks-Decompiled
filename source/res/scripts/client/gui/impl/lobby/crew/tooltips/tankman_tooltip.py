# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/tankman_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.tankman_tooltip_commander_feature import TankmanTooltipCommanderFeature
from gui.impl.gen.view_models.views.lobby.crew.tooltips.tankman_tooltip_model import TankmanTooltipModel
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanRestoreInfo
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import Tankman
from helpers import dependency
from helpers import time_utils
from skeletons.gui.shared import IItemsCache

class TankmanTooltip(ViewImpl):
    __slots__ = ('tankmanID',)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanID, *args, **kwargs):
        self.tankmanID = tankmanID
        settings = ViewSettings(R.views.lobby.crew.tooltips.TankmanTooltip(), args=args, kwargs=kwargs)
        settings.model = TankmanTooltipModel()
        super(TankmanTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankmanTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankmanTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        tankman = self.itemsCache.items.getTankman(self.tankmanID)
        with self.viewModel.transaction() as vm:
            nativeVehicle = self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
            hasPenalty = False
            isInTank = tankman.isInTank
            if isInTank:
                hasPenalty = tankman.isUntrained
            vm.setRole(tankman.role)
            vm.setFullName(tankman.getFullUserNameWithSkin())
            vm.setRankUserName(tankman.rankUserName)
            vm.setIsFemale(tankman.isFemale)
            vm.setRankIcon(tankman.extensionLessIconRank)
            self.__fillVehicleSpecialization(vm.nativeVehicle, nativeVehicle, tankman.roleLevel, hasPenalty=hasPenalty)
            if isInTank:
                vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
                self.__fillVehicleSpecialization(vm.currentVehicle, vehicle, tankman.realRoleLevel.lvl, hasPenalty=hasPenalty)
            if tankman.isDismissed:
                vm.setIsDismissed(True)
                dismissalLength = time_utils.getTimeDeltaTillNow(tankman.dismissedAt)
                tankmenRestoreConfig = self.itemsCache.items.shop.tankmenRestoreConfig
                vm.setSecondsLeftToRestore(tankmenRestoreConfig.billableDuration - dismissalLength)
                vm.setHasFreeRestore(dismissalLength < tankmenRestoreConfig.freeDuration)
                setTankmanRestoreInfo(vm.restoreInfo)
            if tankman.role == Tankman.ROLES.COMMANDER:
                self.__fillCommanderFeatures(vm.getCommanderFeatures())

    def __fillCommanderFeatures(self, features):
        sixthSense = TankmanTooltipCommanderFeature()
        sixthSense.setIcon(R.images.gui.maps.icons.tankmen.skills.medium.commander_sixthSense())
        sixthSense.setDescription(backport.text(R.strings.artefacts.sixthSenseBattleBooster.description.builtinPerkBooster()))
        features.addViewModel(sixthSense)
        commanderBonus = TankmanTooltipCommanderFeature()
        commanderBonus.setIcon(R.images.gui.maps.icons.tankmen.skills.big.commander_bonus())
        commanderBonus.setDescription(backport.text(R.strings.tooltips.tankman.commanderFeatures.commanderBonus()))
        features.addViewModel(commanderBonus)

    @staticmethod
    def __fillVehicleSpecialization(vm, vehicle, level, hasPenalty):
        vm.setSpecializationLevel(level)
        vm.setHasPenalty(hasPenalty)
        vm.setNation(vehicle.nationName)
        for tag in vehicle.tags:
            vm.getTags().addString(tag)

        fillVehicleInfo(vm, vehicle, True)
