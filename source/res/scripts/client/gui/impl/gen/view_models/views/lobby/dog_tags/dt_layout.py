# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/dt_layout.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_component_layout import DtComponentLayout

class DtLayout(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DtLayout, self).__init__(properties=properties, commands=commands)

    @property
    def playerName(self):
        return self._getViewModel(0)

    @property
    def clanTag(self):
        return self._getViewModel(1)

    @property
    def engraving(self):
        return self._getViewModel(2)

    @property
    def inscription(self):
        return self._getViewModel(3)

    @property
    def statTracker(self):
        return self._getViewModel(4)

    @property
    def background(self):
        return self._getViewModel(5)

    def _initialize(self):
        super(DtLayout, self)._initialize()
        self._addViewModelProperty('playerName', DtComponentLayout())
        self._addViewModelProperty('clanTag', DtComponentLayout())
        self._addViewModelProperty('engraving', DtComponentLayout())
        self._addViewModelProperty('inscription', DtComponentLayout())
        self._addViewModelProperty('statTracker', DtComponentLayout())
        self._addViewModelProperty('background', DtComponentLayout())
