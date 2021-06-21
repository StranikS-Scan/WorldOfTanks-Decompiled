# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/vehicle_role_descr_view.py
from constants import ACTIONS_GROUP_TYPE_TO_LABEL, ACTION_TYPE_TO_LABEL, ROLE_TYPE_TO_LABEL
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.tooltips.roles_view_model import RolesViewModel
from gui.impl.gen.view_models.views.lobby.tooltips.role_action_model import RoleActionModel
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from frameworks.wulf import ViewSettings
from items.vehicles import getActionsByRole, getRolesActionsGroups

class VehicleRolesTooltipView(ViewImpl, IPrbListener):

    def __init__(self, *args, **kwargs):
        contentResID = R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView()
        settings = ViewSettings(contentResID)
        settings.model = RolesViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(VehicleRolesTooltipView, self).__init__(settings)

    def _onLoading(self, roleID, *args, **kwargs):
        super(VehicleRolesTooltipView, self)._onLoading(*args, **kwargs)
        roleLabel = ROLE_TYPE_TO_LABEL[roleID]
        rolesToActionsGroups = getRolesActionsGroups()
        actionsGroupLabel = ACTIONS_GROUP_TYPE_TO_LABEL[rolesToActionsGroups[roleID]]
        with self.getViewModel().transaction() as model:
            model.setRoleType(actionsGroupLabel)
            model.setRoleBgImage(R.images.gui.maps.icons.roleExp.actionsTooltip.headerImage.dyn(roleLabel)())
            if self.__isRoleXPPrbActive():
                actions = getActionsByRole(roleID)
                roleActions = model.roleActions
                for action in actions:
                    actionLabel = ACTION_TYPE_TO_LABEL[action]
                    roleAction = RoleActionModel()
                    roleAction.setImage(R.images.gui.maps.icons.roleExp.actions.c_128x128.dyn(actionLabel)())
                    roleAction.setDescription(R.strings.menu.roleExp.action.dyn(actionLabel)())
                    roleActions.addViewModel(roleAction)

                roleActions.invalidate()

    def __isRoleXPPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANKED)
