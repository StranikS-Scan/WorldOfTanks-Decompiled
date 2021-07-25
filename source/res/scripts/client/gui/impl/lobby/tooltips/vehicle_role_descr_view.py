# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/vehicle_role_descr_view.py
from constants import ACTION_TYPE_TO_LABEL, ROLE_TYPE_TO_LABEL
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.tooltips.roles_view_model import RolesViewModel
from gui.impl.gen.view_models.views.lobby.tooltips.role_action_model import RoleActionModel
from gui.prb_control.entities.base.listener import IPrbListener
from frameworks.wulf import ViewSettings
from helpers import dependency
from items.vehicles import getActionsByRole
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache

class VehicleRolesTooltipView(ViewImpl, IPrbListener):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        contentResID = R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView()
        settings = ViewSettings(contentResID)
        settings.model = RolesViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(VehicleRolesTooltipView, self).__init__(settings)

    def _onLoading(self, vehicleCD, *args, **kwargs):
        super(VehicleRolesTooltipView, self)._onLoading(*args, **kwargs)
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        roleLabel = ROLE_TYPE_TO_LABEL[vehicle.role]
        with self.getViewModel().transaction() as model:
            model.setRoleType(roleLabel)
            model.setRoleBgImage(R.images.gui.maps.icons.roleExp.actionsTooltip.headerImage.dyn(roleLabel)())
            if self.__isRoleXP(vehicle):
                actions = getActionsByRole(vehicle.role)
                roleActions = model.roleActions
                for action in actions:
                    actionLabel = ACTION_TYPE_TO_LABEL[action]
                    roleAction = RoleActionModel()
                    roleAction.setImage(R.images.gui.maps.icons.roleExp.actions.c_128x128.dyn(actionLabel)())
                    roleAction.setDescription(R.strings.menu.roleExp.action.dyn(actionLabel)())
                    roleActions.addViewModel(roleAction)

                roleActions.invalidate()

    def __isRoleXP(self, vehicle):
        return self.__rankedController.isRankedPrbActive() and self.__rankedController.isSuitableVehicle(vehicle) is None
