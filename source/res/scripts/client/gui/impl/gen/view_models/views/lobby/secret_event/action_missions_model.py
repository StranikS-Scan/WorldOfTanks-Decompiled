# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_missions_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.mission_model import MissionModel
from gui.impl.gen.view_models.views.lobby.secret_event.tank_model import TankModel

class ActionMissionsModel(ActionMenuModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=3):
        super(ActionMissionsModel, self).__init__(properties=properties, commands=commands)

    @property
    def missionList(self):
        return self._getViewModel(4)

    @property
    def prizeTank(self):
        return self._getViewModel(5)

    def _initialize(self):
        super(ActionMissionsModel, self)._initialize()
        self._addViewModelProperty('missionList', UserListModel())
        self._addViewModelProperty('prizeTank', TankModel())
