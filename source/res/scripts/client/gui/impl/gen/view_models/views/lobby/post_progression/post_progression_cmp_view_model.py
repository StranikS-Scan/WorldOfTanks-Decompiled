# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/post_progression_cmp_view_model.py
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_base_view_model import PostProgressionBaseViewModel
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_compare_model import PostProgressionCompareModel

class PostProgressionCmpViewModel(PostProgressionBaseViewModel):
    __slots__ = ('onExitAction',)

    def __init__(self, properties=6, commands=2):
        super(PostProgressionCmpViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def compareControl(self):
        return self._getViewModel(5)

    def _initialize(self):
        super(PostProgressionCmpViewModel, self)._initialize()
        self._addViewModelProperty('compareControl', PostProgressionCompareModel())
        self.onExitAction = self._addCommand('onExitAction')
