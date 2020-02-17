# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tech_tree/tech_tree_overlay_view_model.py
from frameworks.wulf import ViewModel

class TechTreeOverlayViewModel(ViewModel):
    __slots__ = ('onCloseEvent',)

    def __init__(self, properties=0, commands=1):
        super(TechTreeOverlayViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(TechTreeOverlayViewModel, self)._initialize()
        self.onCloseEvent = self._addCommand('onCloseEvent')
