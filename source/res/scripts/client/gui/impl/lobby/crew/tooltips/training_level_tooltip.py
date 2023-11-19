# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/training_level_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.training_level_modifiers_model import TrainingLevelModifiersModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.training_level_tooltip_model import TrainingLevelTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
MODIFIERS_LOC = R.strings.tooltips.trainingLevel.modifiers

class TrainingLevelTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_tankman',)

    def __init__(self, tankmanId, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.tooltips.TrainingLevelTooltip(), args=args, kwargs=kwargs)
        settings.model = TrainingLevelTooltipModel()
        self._tankman = self._itemsCache.items.getTankman(tankmanId)
        super(TrainingLevelTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TrainingLevelTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TrainingLevelTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIsFemale(self._tankman.isFemale)
            roleLV = vm.getRoles()
            for role in self._tankman.roles():
                roleLV.addString(role)

            modifiersVL = vm.getModifiers()
            self._addModifier(modifiersVL, self._tankman.roleLevel, backport.text(MODIFIERS_LOC.baseLevel()))
            nativeVehicle = self._itemsCache.items.getItemByCD(self._tankman.vehicleNativeDescr.type.compactDescr)
            fillVehicleInfo(vm.nativeVehicle, nativeVehicle, True, nativeVehicle.tags)
            vm.setNation(nativeVehicle.nationName)
            if self._tankman.isInTank:
                vehicle = self._itemsCache.items.getVehicle(self._tankman.vehicleInvID)
                fillVehicleInfo(vm.currentVehicle, vehicle, True, vehicle.tags)
            b = self._tankman.realRoleLevel.bonuses
            if b.commBonus:
                self._addModifier(modifiersVL, b.commBonus, backport.text(MODIFIERS_LOC.commanderBonus()))
            if b.brothersBonus:
                self._addModifier(modifiersVL, b.brothersBonus, backport.text(MODIFIERS_LOC.perks()))
            if b.eqsBonus or b.optDevsBonus:
                self._addModifier(modifiersVL, b.eqsBonus + b.optDevsBonus, backport.text(MODIFIERS_LOC.equipment()))
            if b.penalty:
                self._addModifier(modifiersVL, b.penalty, backport.text(MODIFIERS_LOC.unsuitableSpecialization()))

    @staticmethod
    def _addModifier(modifiersVL, value, reason):
        modifiersModel = TrainingLevelModifiersModel()
        modifiersModel.setValue(round(value, 2))
        modifiersModel.setReason(reason)
        modifiersVL.addViewModel(modifiersModel)
