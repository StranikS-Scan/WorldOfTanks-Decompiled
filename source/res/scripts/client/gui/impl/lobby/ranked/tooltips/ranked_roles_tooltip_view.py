# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/tooltips/ranked_roles_tooltip_view.py
from constants import ACTIONS_GROUP_TYPE_TO_LABEL, ACTION_TYPE_TO_LABEL, ROLE_TYPE_TO_LABEL
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.ranked.tooltips.roles_view_model import RolesViewModel
from gui.impl.gen.view_models.views.lobby.ranked.tooltips.role_action_model import RoleActionModel
from items.vehicles import getRolesActions, getRolesActionsGroups

class RankedRolesTooltipView(ViewImpl):

    def __init__(self, *args, **kwargs):
        contentResID = R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView()
        settings = ViewSettings(contentResID)
        settings.model = RolesViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(RankedRolesTooltipView, self).__init__(settings)

    def _onLoading(self, roleID, *args, **kwargs):
        super(RankedRolesTooltipView, self)._onLoading(*args, **kwargs)
        rolesToActions = getRolesActions()
        roleLabel = ROLE_TYPE_TO_LABEL[roleID]
        rolesToActionsGroups = getRolesActionsGroups()
        actionsGroupLabel = ACTIONS_GROUP_TYPE_TO_LABEL[rolesToActionsGroups[roleID]]
        with self.getViewModel().transaction() as model:
            model.setRoleName(R.strings.menu.roleExp.actionsGroup.dyn(actionsGroupLabel)())
            model.setRoleImage(R.images.gui.maps.icons.roleExp.actionsTooltip.headerImage.dyn(roleLabel)())
            roleActions = model.roleActions
            for action in rolesToActions[roleID]:
                actionLabel = ACTION_TYPE_TO_LABEL[action]
                roleAction = RoleActionModel()
                roleAction.setImage(R.images.gui.maps.icons.roleExp.actions.c_128x128.dyn(actionLabel)())
                roleAction.setDescription(R.strings.menu.roleExp.action.dyn(actionLabel)())
                roleActions.addViewModel(roleAction)

            roleActions.invalidate()
