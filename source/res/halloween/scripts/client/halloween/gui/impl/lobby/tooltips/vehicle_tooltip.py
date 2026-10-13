# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/vehicle_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.crew_presenter import setCrewSlots
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import replaceHyphenToUnderscore
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_tooltip_model import VehicleTooltipModel
from halloween.gui.impl.lobby.hw_helpers import isDailyKeyQuestCompleted, getVehicleState
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class VehicleTooltipView(ViewImpl):
    __slots__ = ('__vehicle',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicleCD, **kwargs):
        settings = ViewSettings(R.views.halloween.mono.lobby.tooltips.vehicle_tooltip())
        settings.model = VehicleTooltipModel()
        settings.kwargs = kwargs
        self.__vehicle = self.__itemsCache.items.getItemByCD(int(vehicleCD))
        super(VehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleTooltipView, self)._onLoading(*args, **kwargs)
        isQuestVisible = kwargs.get('isQuestVisible', False)
        isStatusVisible = kwargs.get('isStatusVisible', False)
        with self.viewModel.transaction() as model:
            model.setVehicleName(replaceHyphenToUnderscore(self.__vehicle.name.replace(':', '-')))
            model.setVehicleType(self.__vehicle.type)
            vehicleState = getVehicleState(self.__vehicle)
            model.setVehicleState(vehicleState.value)
            model.setUserName(self.__vehicle.userName)
            model.setUserDescription(self.__vehicle.longDescriptionSpecial)
            isDailyKeyQuestVisible = isQuestVisible and not isDailyKeyQuestCompleted(self.__vehicle.intCD)
            model.setIsDailyKeyQuestVisible(isDailyKeyQuestVisible)
            model.setIsStatusVisible(isStatusVisible)
            model.setIsElite(self.__vehicle.isPremium)
            slotsVL = model.getCrewSlots()
            setCrewSlots(slotsVL, self.__vehicle)
