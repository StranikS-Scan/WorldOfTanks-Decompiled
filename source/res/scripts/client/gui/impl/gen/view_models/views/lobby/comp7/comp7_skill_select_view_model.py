# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/comp7_skill_select_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.skill_model import SkillModel

class Comp7SkillSelectViewModel(ViewModel):
    __slots__ = ('onClose', 'onSelect', 'onEquip')

    def __init__(self, properties=2, commands=3):
        super(Comp7SkillSelectViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def skills(self):
        return self._getViewModel(0)

    @staticmethod
    def getSkillsType():
        return SkillModel

    @property
    def tankInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getTankInfoType():
        return VehicleModel

    def _initialize(self):
        super(Comp7SkillSelectViewModel, self)._initialize()
        self._addViewModelProperty('skills', UserListModel())
        self._addViewModelProperty('tankInfo', VehicleModel())
        self.onClose = self._addCommand('onClose')
        self.onSelect = self._addCommand('onSelect')
        self.onEquip = self._addCommand('onEquip')
