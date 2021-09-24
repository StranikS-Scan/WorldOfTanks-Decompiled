# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_multiopen_renderer_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_bonus_model import WtBonusModel

class WtEventMultiopenRendererModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtEventMultiopenRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    def getHasSpecialVehicle(self):
        return self._getBool(1)

    def setHasSpecialVehicle(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(WtEventMultiopenRendererModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addBoolProperty('hasSpecialVehicle', False)
