# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/tooltips/roles_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.ranked.tooltips.role_action_model import RoleActionModel

class RolesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RolesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def roleActions(self):
        return self._getViewModel(0)

    def getRoleName(self):
        return self._getResource(1)

    def setRoleName(self, value):
        self._setResource(1, value)

    def getRoleImage(self):
        return self._getResource(2)

    def setRoleImage(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(RolesViewModel, self)._initialize()
        self._addViewModelProperty('roleActions', UserListModel())
        self._addResourceProperty('roleName', R.invalid())
        self._addResourceProperty('roleImage', R.invalid())
