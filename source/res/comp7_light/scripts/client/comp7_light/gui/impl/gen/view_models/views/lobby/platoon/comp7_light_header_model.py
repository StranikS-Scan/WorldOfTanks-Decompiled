# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/platoon/comp7_light_header_model.py
from gui.impl.gen.view_models.views.lobby.platoon.member_count_dropdown import MemberCountDropdown
from gui.impl.gen.view_models.views.lobby.platoon.window_header_model import WindowHeaderModel

class Comp7LightHeaderModel(WindowHeaderModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(Comp7LightHeaderModel, self).__init__(properties=properties, commands=commands)

    @property
    def memberCountDropdown(self):
        return self._getViewModel(7)

    @staticmethod
    def getMemberCountDropdownType():
        return MemberCountDropdown

    def _initialize(self):
        super(Comp7LightHeaderModel, self)._initialize()
        self._addViewModelProperty('memberCountDropdown', MemberCountDropdown())
