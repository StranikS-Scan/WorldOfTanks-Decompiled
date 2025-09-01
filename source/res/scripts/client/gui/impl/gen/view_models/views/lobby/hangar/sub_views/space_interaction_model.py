# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/space_interaction_model.py
from frameworks.wulf import ViewModel

class SpaceInteractionModel(ViewModel):
    __slots__ = ('onMoveSpace', 'onMouseOver3dScene')

    def __init__(self, properties=0, commands=2):
        super(SpaceInteractionModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(SpaceInteractionModel, self)._initialize()
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
