# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/comp7_header_model.py
from gui.impl.gen.view_models.views.lobby.platoon.comp7_member_count_dropdown import Comp7MemberCountDropdown
from gui.impl.gen.view_models.views.lobby.platoon.window_header_model import WindowHeaderModel

class Comp7HeaderModel(WindowHeaderModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(Comp7HeaderModel, self).__init__(properties=properties, commands=commands)

    @property
    def memberCountDropdown(self):
        return self._getViewModel(7)

    @staticmethod
    def getMemberCountDropdownType():
        return Comp7MemberCountDropdown

    def _initialize(self):
        super(Comp7HeaderModel, self)._initialize()
        self._addViewModelProperty('memberCountDropdown', Comp7MemberCountDropdown())
