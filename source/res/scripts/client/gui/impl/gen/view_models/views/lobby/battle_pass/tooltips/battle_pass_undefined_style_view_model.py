# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_undefined_style_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.style_option_model import StyleOptionModel

class BattlePassUndefinedStyleViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattlePassUndefinedStyleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def options(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(BattlePassUndefinedStyleViewModel, self)._initialize()
        self._addViewModelProperty('options', UserListModel())
