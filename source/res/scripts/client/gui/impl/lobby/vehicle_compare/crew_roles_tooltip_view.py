# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/crew_roles_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_compare.tooltips.crew_roles_tooltip_view_model import CrewRolesTooltipViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.tooltips.crew_member_model import CrewMemberModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class CrewRolesTooltipView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__vehicle',)

    def __init__(self, vehicle):
        settings = ViewSettings(R.views.lobby.vehicle_compare.tooltips.CrewRolesTooltip())
        settings.model = CrewRolesTooltipViewModel()
        self.__vehicle = vehicle
        super(CrewRolesTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewRolesTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CrewRolesTooltipView, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setVehicleName(self.__vehicle.descriptor.type.shortUserString)
            crew = vm.getCrew()
            for _, tankman in self.__vehicle.crew:
                crewMember = CrewMemberModel()
                crewMember.setRole(tankman.role)
                additionalRoles = crewMember.getAdditionalRoles()
                for additionalRole in tankman.roles():
                    if additionalRole != tankman.role:
                        additionalRoles.addString(additionalRole)

                crew.addViewModel(crewMember)
